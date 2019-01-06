# Cat Tracker

This code is a combination of two examples that came with the AIY Vision Kit that will find a cat on the camera live stream, center a turret in the middle of it, and, after a certain period of time, trigger a pump to spray water at the cat.

## To Use
Place files in ~/AIY-projects-python/src/examples/vision/ on your AIY Raspberry Pi. Be warned that this code tends to overheat the Pi, so it may be better to use it with the box open and with good air flow. I also did the suggestions added [here](https://github.com/google/aiyprojects-raspbian/issues/346#issuecomment-392221590) to prevent it from freezing constantly.

The `object_detection_camera.py` will do the detection without the servo. This is better for playing around, as you will get errors about pin in use and similar that will prevent the program from running. Once you have a servo hooked up, feel free to adjust the pins and use `object_detection_servo_camera.py`

Kit information: https://aiyprojects.withgoogle.com/vision/
Code: https://github.com/google/aiyprojects-raspbian

## Code Examples Used
### Object Detection 
https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/src/examples/vision/object_detection.py 
https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/src/aiy/vision/models/object_detection.py
This model and code example looks for three things - person, dog, or cat. This was perfect for this project, and thus prevented me from needing to train my own model. The only limitation is the code runs off of an image input, not a stream from the camera.

### Face Detection from Camera
https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/src/examples/vision/face_detection_camera.py
This example finds faces and draws a bounding box around them. By using this example with the above model, I was able to get what I needed in a short period of time for a hackathon, with no prior experience in computer vision!

## Turret Information
https://www.thingiverse.com/thing:1068151
Coming soon~