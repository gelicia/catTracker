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
from PIL import Image
from PIL import ImageDraw

from aiy.vision.inference import CameraInference
from aiy.vision.models import object_detection
from examples.vision.annotator import Annotator
from picamera import PiCamera

def crop_center(image):
    width, height = image.size
    size = min(width, height)
    x, y = (width - size) / 2, (height - size) / 2
    return image.crop((x, y, x + size, y + size)), (x, y)

def read_stdin():
    return io.BytesIO(sys.stdin.buffer.read())


def main():
    """Face detection camera inference example."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_frames', '-n', type=int, dest='num_frames', default=None,
        help='Sets the number of frames to run for, otherwise runs forever.')
    args = parser.parse_args()

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
                    annotator.bounding_box(transform(obj.bounding_box), fill=0 , outline=outlineColor)
                    annotator.text(textXYTransform(obj.bounding_box), "person" if obj.kind == 1 else "cat" if obj.kind == 2 else "dog" if obj.kind == 3 else "other", color=outlineColor)

                annotator.update()

        camera.stop_preview()


if __name__ == '__main__':
    main()