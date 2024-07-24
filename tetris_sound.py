import os
import numpy as np
import cv2 as cv
import tesserocr
from tesserocr import PyTessBaseAPI
from pydub import AudioSegment

from tkinter import ttk
from tkinter import Tk
from tkinter import filedialog as fd
from tkinter import StringVar

from ffmpeg import FFmpeg

start_pixel = None
end_pixel = None
flashing_pixel = None
video_file = None
output_dir = ""
line_count = 0
previous_line_count = 0
frame_count = 0
timestamps = []

def choose_video():
    global output_dir
    video_file.set(fd.askopenfilename())
    output_dir = os.path.join(os.path.dirname(video_file.get()), '')
    print(output_dir)

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def choose_pixel(event,x,y,flags,param):
    global start_pixel
    global end_pixel
    if event == cv.EVENT_LBUTTONUP:
        if start_pixel == None:
            start_pixel = [x, y]
            print(f"start point {[x, y]}")
        else:
            end_pixel = [x, y]
            print(f"end point {[x, y]}")

def opencv_pick_linebox(video):
    curr_frame = 0
    ret, frame = video.read()
    cv.imshow("pick_pixel", frame)
    cv.setMouseCallback("pick_pixel",choose_pixel)
    while True:
        if cv.waitKey(1) == ord('q'):
            cv.destroyWindow("pick_pixel")
            break
        elif cv.waitKey(1) == ord('n'):
            curr_frame += 20
            video.set(cv.CAP_PROP_POS_FRAMES, curr_frame - 1)
            ret, frame = video.read()
            cv.imshow('pick_pixel', frame)

def click_flashing_pixel(event,x,y,flags,param):
    global flashing_pixel
    if event == cv.EVENT_LBUTTONUP:
        flashing_pixel = [x, y]
        print(f"clicked in {flashing_pixel}")

def opencv_pick_flashing_pixel(video):
    curr_frame = 0
    ret, frame = video.read()
    cv.imshow("pick_pixel", frame)
    cv.setMouseCallback("pick_pixel",click_flashing_pixel)
    while True:
        if cv.waitKey(1) == ord('q'):
            cv.destroyWindow("pick_pixel")
            break
        elif cv.waitKey(1) == ord('n'):
            curr_frame += 20
            video.set(cv.CAP_PROP_POS_FRAMES, curr_frame)
            ret, frame = video.read()
            cv.imshow('pick_pixel', frame)

def save_video():
    global timestamps
    global video_file

    if not timestamps:
        return
    print(f"reading tetris audio effect from file {resource_path('nes.mp3')}")
    song = AudioSegment.from_file(resource_path("nes.mp3"))
    final_audio = AudioSegment.empty()
    prev_timestamp = 0
    for time in timestamps:
        final_audio += AudioSegment.silent(duration=(time - prev_timestamp))
        final_audio += song
        prev_timestamp = time + len(song)

    print(f"writing audio track to file {resource_path('final.mp3')}...")
    file_handle = final_audio.export(resource_path("final.mp3"), format="mp3")

    print(f"starting ffmpeg. Will write to {output_dir}video_with_tetris_sound_effect.mp4")
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input(video_file.get())
        .input(resource_path("final.mp3"))
        .output(
            output_dir + "video_with_tetris_sound_effect.mp4",
            {"codec:v": "copy"},
            map=["0:v:0", "1:0"],
            crf=24,
        )
    )
    ffmpeg.execute()


def detect_by_ocr(video):
    time = 0
    global timestamps, line_count, previous_line_count, start_pixel, end_pixel, frame_count

    with PyTessBaseAPI(path=resource_path(""),lang='eng', psm=tesserocr.PSM.SINGLE_LINE) as api:
        while video.isOpened():
            ret, frame = video.read()

            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            frame = frame[start_pixel[1]:end_pixel[1], start_pixel[0]:end_pixel[0]]
            blur = cv.blur(frame,(5,5))
            gray = cv.cvtColor(blur , cv.COLOR_BGR2GRAY)
            gray = 255 - gray
            #thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]
            #kernel = np.ones((5,5),np.uint8)
            #opening = cv.morphologyEx(gray, cv.MORPH_OPEN, kernel)

            api.SetVariable("tessedit_char_whitelist", "0123456789");
            api.SetVariable('debug_file', '/dev/null')

            img_bytes = gray.tobytes()
            api.SetImageBytes(
                imagedata=img_bytes,
                width=gray.shape[1],
                height=gray.shape[0],
                bytes_per_pixel=1,
                bytes_per_line=gray.shape[1])

            text = api.GetUTF8Text()
            #print(f"Text = {text}")
            if text != "":
                try:
                    previous_line_count = line_count
                    line_count = int(text)
                    #print(f"Lines = {line_count:03d}")
                except:
                    pass

            current_time = video.get(cv.CAP_PROP_POS_MSEC) - 350 # offset because the sound comes before the line update
            if previous_line_count + 4 == line_count:
                print(f"Tetris!! {current_time}")
                time = current_time
                timestamps.append(time)

            cv.imshow('frame', gray)

            if cv.waitKey(1) == ord('q'):
                break
            frame_count = frame_count + 3
            video.set(cv.CAP_PROP_POS_FRAMES, frame_count)

def detect_by_flash(video):
    global timestamps, flashing_pixel
    time = 0

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        current_color_r = int(frame[flashing_pixel[1], flashing_pixel[0], 0])

        current_time = video.get(cv.CAP_PROP_POS_MSEC)
        if current_color_r >= 245 and (time + 2000) <= current_time:
            print(f"Tetris!! {current_time}")
            time = current_time
            timestamps.append(time)

        cv.imshow('frame', gray)
        if cv.waitKey(1) == ord('q'):
            break

    video.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    root = Tk()
    frm = ttk.Frame(root, padding=10)
    style = ttk.Style(root)
    style.theme_use("clam")

    video_file = StringVar()
    selected_detection_method = StringVar()
    methods = (('Flash', 'F'), ('Line Count', 'L'))

    label = ttk.Label(text="Tetris detection method:")
    label.pack(padx=5, pady=5)
    for method in methods:
        r = ttk.Radiobutton(
            root,
            text=method[0],
            value=method[1],
            variable=selected_detection_method
        )
        r.pack()

    label_video = ttk.Label(text="Video file:")
    label_video.pack(padx=5, pady=5)
    label_file = ttk.Label(textvariable=video_file)
    label_file.pack(padx=5, pady=5)
    btn_choose_video = ttk.Button(text="Choose video file", command=choose_video)
    btn_choose_video.pack(padx=10, pady=10)
    btn_pixel_select = ttk.Button(text="Go to pixel selection...", command=root.destroy)
    btn_pixel_select.pack(padx=10, pady=10)

    root.mainloop()
    video = cv.VideoCapture(video_file.get())

    if selected_detection_method.get() == "L":
        opencv_pick_linebox(video)
        detect_by_ocr(video)
    else:
        opencv_pick_flashing_pixel(video)
        detect_by_flash(video)

    save_video()

    video.release()
    cv.destroyAllWindows()
