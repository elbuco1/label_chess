import cv2


def frames_from_video_generator(video_path, fps_ratio):
    """Load frames from a video in memory.

    Args:
        video_path (str): path to video
        fps_ratio (int): only 1/fps_ratio frames are kept
        new_fps (int): desired fps for the frames. Only one frame
            in every old_fps/new_fps is kept.

    Returns:
        list: list of frames
    """
    frame_number = 0

    cap = cv2.VideoCapture(video_path)
    print("Loading frames.")
    while True:
        ret, frame = cap.read()
        if ret:
            if frame_number % fps_ratio == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                yield frame
            frame_number += 1
        else:
            break
    cap.release()


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
