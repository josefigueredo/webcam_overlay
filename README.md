# webcam_overlay

Motivations: Whenever I share (present) my screen in google meet the viewers maximize the window and the webcams view hide.
I try using OBS but the resolution of the webcam view is 720px max. The work arround that I find was to create a transparent circular overlay window to achieve that.

## How to run it

```python
python3 overlaycam.py
```

## How it works

At start it will detect your available webcams. I have the laptops built in and an usb with higher resolution.
If you press the mouse right button it will cycle webcam sources.
If you press the mouse middle button it will toggle black and white.

## Dependencies

- Computer Vision
- QT5
- Numpy
- PIL

## Screenshot

![screenshot](sreenshot.png "Screenshot")
