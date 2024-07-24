# tetris-sound
Reads a NES Tetris video and adds only the Tetris sound effect.

### usage
- Select either detection by flashing pixel or by line count OCR (flashing is much faster)
- Use the file dialog to select the video file, and press "Go to pixel selection..."
- Depending on which method you chose, click on the flashing pixel or on the top-left and bottom-right corners of the line count number box
<img src="https://github.com/user-attachments/assets/2fc76ae0-5708-4595-b7a5-5dfbf16b6e90" width="300"/>

(this is just for illustration, the points ain't drawn on the screen yet)
- If needed you can go forward on the video by pressing 'n', press 'q' when you are done (might have to press a few times for some reason)
- This window will close and another one will appear playing the video and detecting tetrises, when it finishes, it will automatically create a file named "video_with_tetris_sound_effect.mp4" with a copy of the video and the tetris sounds.

### Running

An initial version, only with the flashing detection method, is available [here](https://github.com/brianch/tetris-sound/actions/runs/10062817898), the later builds aren't working yet (they are not bundling everything needed). 

If you want to run it from the python file, install tesserocr, download the repository and run:

```
python3 -m venv venv
source venv/bin/activate (on Windows run venv\Scripts\activate.bat)
pip install -r requirements.txt
python tetris_sound.py
```

Note: FFmpeg has to be on your path in either case as of now.

(I'm not very familiar with python (or openCV and OCR), so the code is a bit of a mess)

#### License

This project is under the GPLv2 or later.

The file eng.traineddata was added here for convenience, it is from [this repository](https://github.com/tesseract-ocr/tessdata_fast) and is under the Apache-2.0 license.
