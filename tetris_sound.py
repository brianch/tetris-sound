import os
import numpy as np
import cv2 as cv
#import soundfile as sf
from pydub import AudioSegment

from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import StringVar

from ffmpeg import FFmpeg

pixel = [0, 0]
video_file = None
output_dir = ""

def choose_video():
    global output_dir
    video_file.set(fd.askopenfilename())
    output_dir = os.path.join(os.path.dirname(video_file.get()), '')
    print(output_dir)


def choose_pixel(event,x,y,flags,param):
    global pixel
    if event == cv.EVENT_LBUTTONUP:
        pixel = [x, y]
        print(f"clicked in {pixel}")

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    root = Tk()
    video_file = StringVar()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    ttk.Label (frm, text="Video:").grid(column=0, row=0)
    ttk.Label (frm, textvariable=video_file).grid(column=1, row=0)

    ttk.Button(frm, text="Choose video file", command=choose_video).grid(column=0, row=1)

    ttk.Button(frm, text="Go to pixel selection...", command=root.destroy).grid(column=0, row=2)

    root.mainloop()

    #video = cv.VideoCapture('/home/brian/Vídeos/tetris/Tetris (USA)-240210-001358-818k.m4v')
    video = cv.VideoCapture(video_file.get())

    #fps = video.get(cv.CAP_PROP_FPS)
    #frame_count = int(video.get(cv.CAP_PROP_FRAME_COUNT))
    #video_duration = frame_count/fps

    time = 0
    timestamps = []
    #fps = video.get(cv.CV_CAP_PROP_FPS)
    amount_of_frames = video.get(cv.CAP_PROP_FRAME_COUNT)
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
    print(f"Pixel [{pixel}")

    while video.isOpened():
        ret, frame = video.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        #278, 288
        current_color_r = int(frame[pixel[1], pixel[0], 0])
        #g = int(frame[pixel[1], pixel[0], 1])
        #r = int(frame[pixel[1], pixel[0], 2])

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

    print(f"reading tetris audio effect from file {resource_path("nes.mp3")}")
    song = AudioSegment.from_file(resource_path("nes.mp3"))
    final_audio = AudioSegment.empty()
    prev_timestamp = 0
    for time in timestamps:
        final_audio += AudioSegment.silent(duration=(time - prev_timestamp))
        final_audio += song
        prev_timestamp = time + len(song)

    print(f"writing audio track to file {resource_path("final.mp3")}...")
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
            map=["0:0", "1:0"],
            #map=["0:0", "1:1"],
            crf=24,
        )
    )
    ffmpeg.execute()
