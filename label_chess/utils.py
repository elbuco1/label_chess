#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
from functools import lru_cache


def frames_from_video_generator(video_path, fps_ratio):
    """Load frames from a video in memory.

    Args:
        video_path (str): path to video
        fps_ratio (int): only 1/fps_ratio frames are kept
        new_fps (int): desired fps for the frames. Only one frame
            in every old_fps/new_fps is kept.

    Returns:
        list: list of frames
        int: frame number
    """
    frame_number = 0

    cap = cv2.VideoCapture(video_path)
    print("Loading frames.")
    while True:
        ret, frame = cap.read()
        if ret:
            if frame_number % fps_ratio == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                yield [frame, frame_number]
            frame_number += 1
        else:
            break
    cap.release()

def frame_id_generator(video, fps_ratio=1):
    """ Generator of frame positions with a
    fixed offset.
    """
    nb_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(0, nb_frames, fps_ratio):
        yield i 

def get_video_frame(video, frame_id, last_frame_id = 0):
    """ Get a specific frame from a video
    Args:
        video (cv2.VideoCapture)
        frame_id (int): frame position
        last_frame_id (int): last frame position pass to the function.
            setting the position is expensive. this gives the possibility
            to not set the pos.
    """
    if frame_id - last_frame_id != 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)

    ret, frame = video.read() 

    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    return None


def load_video(video_path):
    video = cv2.VideoCapture(video_path)
    return video


def resize_image(image, expected_height):
    """Resize PIL image to expected height
    while maintaining the aspect ratio

    Args:
        image (PIL.Image)
        expected_height (int): expected height of the
            image
    Returns:
        PIL.Image: image
    """
    height_percent = (expected_height / float(image.size[1]))
    width_size = int((float(image.size[0]) * float(height_percent)))
    image = image.resize((width_size, expected_height))
    return image
