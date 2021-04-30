from pytube import YouTube
import requests
import os
import cv2


def download_video(url, save_path, file_name,
                   file_extension="mp4", res="720p"):
    """From the url of a youtube video, download the video
    only (no soundtrack).

    As a default, the video is downloaded as mp4 format with a
    resolution of 720p.
    If requested resolution is not available, the higher resolution
    available is downloaded.

    Args:
        url (str): youtube video url
        save_path (str): directory to save downloaded video
        file_name (str): name under which to save the video file
        file_extension (str, optional): Which video type to download. Defaults to "mp4".
        res (str, optional): Which video resolution to download. Defaults to "720p".
    """
    yt = YouTube(url)

    stream = yt.streams.filter(
        type="video",
        adaptive=True,
        file_extension=file_extension,
        res=res)

    # if res not available
    # take higher res available
    if len(stream) == 0:
        stream = yt.streams.filter(
            type="video",
            adaptive=True,
            file_extension=file_extension,
        )

    stream = stream.order_by(
        'resolution')
    stream = stream.desc().first()

    path = os.path.join(save_path, f"{file_name}.{file_extension}")
    print(
        f"Downloading video at url {url},"
        f" to {path}."
    )
    stream.download(
        output_path=save_path,
        filename=file_name
    )
    print("Done.")


def download_fen(url, save_path, file_name, base_url="https://www.chessgames.com/pgn"):
    """Download a pgn file from www.chessgames.com.

    Args:
        url (str): pgn file url must be [base_url]/url
        save_path (str):  directory to save downloaded pgn file
        file_name (str): name to give to the downloaded pgn file
        base_url (str, optional): default url prefix for chessgames.com.
            If not adequate, pass full url to [url] and empty string
            to [base_url] Defaults to "https://www.chessgames.com/pgn".
    """
    url = os.path.join(base_url, url)
    save_path = os.path.join(save_path, file_name)

    print(
        f"Downloading pgn at url {url},"
        f" to {save_path}."
    )

    r = requests.get(url, allow_redirects=True)
    with open(save_path, 'wb') as f:
        f.write(r.content)

    print("Done.")


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

# def main():
#     video_url = "https://www.youtube.com/watch?v=tmMKi7JPAZg"
#     # https://www.chessgames.com/pgn/carlsen_kramnik_2019.pgn?gid=1988407
#     pgn_url = "carlsen_kramnik_2019.pgn?gid=1988407"
#     save_path = "data/raw"
#     file_name = "kramnik_carlsen_salman2019"

#     os.makedirs(save_path, exist_ok=True)
#     # download_video(
#     #     url=url,
#     #     save_path=save_path,
#     #     file_name=file_name
#     # )

#     download_fen(pgn_url, save_path, file_name)


# if __name__ == "__main__":
#     main()
