#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Camera inference object detection demo code.

Example
object_detection_camera.py --num_frames 10
"""
import argparse
import io
import sys
import math
import time
from PIL import Image
from PIL import ImageDraw

from aiy.vision.inference import CameraInference
from aiy.vision.models import object_detection
from examples.vision.annotator import Annotator
from picamera import PiCamera
from gpiozero import AngularServo
from gpiozero import DigitalOutputDevice
from aiy.vision.pins import PIN_A
from aiy.vision.pins import PIN_B
from aiy.vision.pins import PIN_C

def read_stdin():
    return io.BytesIO(sys.stdin.buffer.read())

def rangeConvert(value, from_min, from_max, new_min, new_max):
    return ( (value - from_min) / (from_max - from_min) ) * (new_max - new_min) + new_min

def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def main():
    """object detection camera inference example."""
    parser = argparse.ArgumentParser()
    countdown = 20
    parser.add_argument('--num_frames', '-n', type=int, dest='num_frames', default=None,
        help='Sets the number of frames to run for, otherwise runs forever.')
    args = parser.parse_args()
    
    servoX = AngularServo(PIN_B)
    servoY = AngularServo(PIN_A)
    relay = DigitalOutputDevice(PIN_C, active_high=True, initial_value=True)
    #relay.blink(n=1)
    relay.blink(on_time=0.05, n=1)

    # Forced sensor mode, 1640x1232, full FoV. See:
    # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
    # This is the resolution inference run on.
    with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=10) as camera:
        camera.start_preview()

        # Annotator renders in software so use a smaller size and scale results
        # for increased performace.
        annotator = Annotator(camera, dimensions=(320, 240))
        scale_x = 320 / 1640
        scale_y = 240 / 1232

        # Incoming boxes are of the form (x, y, width, height). Scale and
        # transform to the form (x1, y1, x2, y2).
        def transform(bounding_box):
            x, y, width, height = bounding_box
            return (scale_x * x, scale_y * y, scale_x * (x + width),
                    scale_y * (y + height))
        
        def textXYTransform(bounding_box):
            x, y, width, height = bounding_box
            return (scale_x * x, scale_y * y)

        with CameraInference(object_detection.model()) as inference:
            for result in inference.run():
                objs = object_detection.get_objects(result, 0.3);
                annotator.clear()
                for obj in objs:
                    # blue for person, green for cat, purple for dog, red for anything else
                    outlineColor = "blue" if obj.kind == 1 else "green" if obj.kind == 2 else "purple" if obj.kind == 3 else "red"
                    print(obj.kind)
                    tBoundingBox = transform(obj.bounding_box)
                    annotator.bounding_box(tBoundingBox, fill=0 , outline=outlineColor)
                    annotator.text(textXYTransform(obj.bounding_box), "person" if obj.kind == 1 else "cat" if obj.kind == 2 else "dog" if obj.kind == 3 else "other", color=outlineColor)
                    
                    if len(objs) == 1:
                        x1, y1, x2, y2 = transform(obj.bounding_box)
                        midX = ((x2-x1) / 2) + x1
                        midY = ((y2-y1) / 2) + y1
                        servoPosX = remap(midX, 0, 320, 75, -75)
                        servoPosY = remap(midY, 0, 240, -90, 80) # 90 is low, -90 is high
                        servoPosX = min(90, servoPosX)
                        servoPosX = max(-90, servoPosX)
                        servoPosY = min(90, servoPosY)
                        servoPosY = max(-90, servoPosY)
                        print("x", midX, servoPosX)
                        print("y", midY, servoPosY)
                        servoX.angle = servoPosX
                        servoY.angle = servoPosY
                        
                        countdown-=1
                        
                        if countdown == -1:
                            # squirt
                            annotator.text((midX, midY), "Squirt!!",  color=outlineColor)
                            relay.blink(on_time=0.5, n=1)
                            countdown = 20
                        else:
                            annotator.text((midX, midY), str(countdown),  color=outlineColor)
                if len(objs) == 0:
                    countdown = 20
                annotator.update()

        camera.stop_preview()


if __name__ == '__main__':
    main()