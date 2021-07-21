# Label chess

## Description

Desktop application to get pairs of chess board picture and FEN representation from a chess game video and its corresponding PGN encoding.

Aimed at building a dataset to train machine learning models on the task of predicting a FEN representation given a real life picture of a chess board.

## Use case


### Add files to database



* Download the app from the latest available release on github (you may need to give the execution rights to the app file).
* Download a video of a chess game (i.e. from youtube).
* Download the corresponding pgn file (i.e. from chessgames.com).
* Start the app.
* Add the downloaded pgn file to the app database (i.e. click on the ``Add pgn`` button and follow the instructions).
* Add the downloaded video file to the app database (i.e. click on the ``Add video`` button and follow the instructions).

Note: You can add as many pgn and video files to the app database.

### Start an annotation

<div align='center'>
<img src="demo1.gif"></img>
</div>

* Select a video from the list available videos (i.e. click on the ``Select video...`` button).
* Select a pgn file from the list available pgn files (i.e. click on the ``Select pgn...`` button).
* Select a downsampling ratio for the video (i.e. click on the ``FPS ratio...`` button). Only 1/fps_ratio frame will presented to you during the annotation (where fps_ratio is the selected value).
*  Start an annotation (click on the ``Start`` button).


### Annotation

<div align='center'>
<img src="demo2.gif"></img>
</div>

* A visual representation of the first position in the pgn file is loaded on the left part of the screen whereas the first frame of the video is loaded on the right part of the screen.

* You can go to the next frame by pressing the ``Next`` button or the ``right arrow`` key.
* You can go to the previous frame by pressing the ``Previous`` button or the ``left arrow`` key.
* Once the position displayed on the left part of the screen matches the actual position on the frame, you can save the pair by pressing the ``Save`` button or the ``up arrow`` key.
* You can cancel the last save by pressing the ``Unsave`` button or the ``down arrow`` key.
* If there is no good frame available for a given position, you can skip the currently displayed position by pressing the ``Skip`` button or the space bar.
* You can select a part of the frame.
* To cancel the current annotation, click the ``Cancel`` button.
* Once you are done with the annotation, save it by pressing the ``End`` button. You will be prompted for a name to give your annotation.

Saved annotations are persisted in the app database and can be recovered after stopping/starting the app.

### Export annotation

<div align='center'>
<img src="demo3.gif"></img>
</div>

You can export one or more annotations by clicking on the ``Export`` button.

The annotations are exported using csv files.

The main file lists the exported annotations along with the video url and the name of the annotation file for each of the selected annotations.

There is one separate csv file per annotation. Each row contains the following information:

* video frame id
* corresponding fen encoding
* top left corner of the selected part of the video frame (coordinates expressed in percentage of the frame dimensions)
* bottom right corner of the selected part of the video frame


### Database management

The database and its artefacts are stored under the ``~/label_chess_database``.

When running the application for the first time, click on the ``Reset DB`` button.

You can clear the app database and delete its artefacts by clicking on the ``Reset DB`` button.



### Use this work

You can use this work for non-commercial use.

If you use to produce an academic paper, please refer to this work.


### Release

The app has been released using the latest ubuntu version to date (20.04). Therefore there is no guarantee it works on other OS.

### Build it yourself

Use the script ``pyinstaller.sh``. You can use the ``.github/workflows/push_on_main.yaml`` as an example.