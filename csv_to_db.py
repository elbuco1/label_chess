from builtins import Exception
import pandas as pd
import os
from label_chess import models
import subprocess
import requests
import traceback

def parse_csv(file_path):
    """Load csv file and aggregate meatadata to
    create a single game identifier.

    Args:
        file_path (str): path to csv file.
            Must contain the following fields:
            "video_url", "pgn_url", "event",
            "white_player", "black_player",
            "round"

    Returns:
        pandas.DataFrame: three columns:
            video_url, pgn_url and play_id
    """
    df = pd.read_csv(file_path)
    keep_columns = [
        "video_url",
        "pgn_url",
        "event",
        "white_player",
        "black_player",
        "round"
    ]
    df = df.loc[:, keep_columns]

    play_columns = [
        "event",
        "white_player",
        "black_player",
        "round"
    ]
    df.loc[:, "round"] = df.loc[:, "round"].astype(str)
    df.loc[:,"play_id"] = df.loc[:,play_columns].apply(
        lambda x: '_'.join(x), axis=1 )
    
    df = df.drop(play_columns, axis=1)
    return df

def remove_exists(path):
    if os.path.exists(path):
        os.remove(path)


def download_video(url, destination_dir, play_name):
    """Download video from given url (not tested for other
    than youtube videos). Video is saved under
    destination_dir/play_name.mp4.

    MP4 video without audio is downloaded.
    Quality is either 360p, 480p or 720p. The lowest available is
    the one selected.

    If download is interrupted partial video file is removed.

    Args:
        url (str): video url
        destination_dir (str): directory to save video
        play_name (str): video file name on disk

    Returns:
        str: path of the downloaded video.
            None if failure.
    """
    save_path = os.path.join(destination_dir, 
        f"{play_name}.mp4")

    remove_exists(save_path)

    cmd = f"youtube-dl {url} "
    cmd += "--rm-cache-dir --no-part "
    cmd += f"-o {save_path} "
    # 360p or 480p or 720p (priority order)
    cmd += "-f 134/135/136"
    print(f"Download video {url} to {save_path}")
    try:
        subprocess.run(cmd, shell=True, capture_output=False)
    except (Exception, KeyboardInterrupt) as e:
        remove_exists(save_path)
        raise e
    return save_path

def download_file_http(url, save_path):
    with requests.get(url, stream=True) as r, open(save_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)

def download_pgn(url, destination_dir, play_name):
    """Download pgn file from given url.

    If download is interrupted partial  file is removed.

    Args:
        url (str): pgn url
        destination_dir (str): directory to save pgn file
        play_name (str): pgn file name on disk

    Returns:
        str: path of the downloaded pgn.
            None if failure.
    """
    save_path = os.path.join(destination_dir, 
        f"{play_name}.pgn")

    remove_exists(save_path)
    print(f"Download pgn {url} to {save_path}")
    
    try:
        download_file_http(url, save_path)
    except (Exception, KeyboardInterrupt) as e :
        remove_exists(save_path)
        raise e

    return save_path

def exists_in_db(url, name, data_type):
    """Check if file url or name is already
    in database.

    Args:
        url (str)
        name (str)
    """
    db = models.get_db()
    urls = db.query(data_type.url).all()
    names = db.query(data_type.name).all()

    urls = {e[0] for e in urls}
    names = {e[0] for e in names}

    return url in urls or name in names

def add_to_db(obj, original_path, db_path):
        """Add file object to db.
        Copy file to app storage.

        Args:
            obj (models.*): ORM object
            original_path (str): path to the video file
            db_path (str): path where to copy the video
                file.
        """
        db = models.get_db()
        db.add(obj)
        db.commit()

def add_job(video_url, pgn_url , game_id):
    """Download pgn and video file and add them to
    the app's database.

    Args:
        video_url (str)
        pgn_url (str)
        game_id (str)
    """
    video_exists = exists_in_db(
        url=video_url, name=game_id, data_type=models.Video)

    pgn_exists = exists_in_db(
        url=pgn_url, name=game_id, data_type=models.PGN)

    if not( video_exists or pgn_exists):

        video_path = download_video(video_url, models.VIDEO_DATA_DIR, game_id)
        pgn_path = download_pgn(pgn_url, models.PGN_DATA_DIR, game_id)

        video = models.Video(
            url = video_url,
            original_path = "",
            path=video_path,
            name=f"{game_id}.mp4"
        )
        pgn = models.PGN(
            url = pgn_url,
            original_path = "",
            path=pgn_path,
            name=f"{game_id}.pgn"
        )

        db = models.get_db()
        db.add(video)
        db.add(pgn)
        db.commit()


# TODO: parallelize
def run_jobs(jobs):
    for i, (video_url, pgn_url, game_id) in enumerate(jobs):
        print(f"Adding {game_id}.")
        game_id = f"{i}.{game_id}"
        try:
            add_job(video_url, pgn_url, game_id)
            print(f"--- Succeeded")
        except (Exception, KeyboardInterrupt) :
            traceback.print_exc()
            print(f"--- Failed")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Add games to db.')
    parser.add_argument('csv_path', type=str, 
                        help='Path to games list.')

    args = parser.parse_args()

    df = parse_csv(args.csv_path)
    df = df.iloc[:3] 

    jobs = ( df.iloc[i]  for i in range(len(df)))

    run_jobs(jobs)


if __name__ == "__main__":
    main()