#!/usr/bin/env python3
""" An audio recoding module for collecting datasets in tigrigna
    it can be used to any other language. the data is taken
    from the WORDS list by modifiying it, it can be applied to any
    language

"""
import pyaudio
import wave
import os
import threading
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np
from time import sleep
import webbrowser
from utils import word_generator, create_csv, update_csv

CSV_HEADERS = ["Tigrigna", "English", "file_name"]
CSV_FILENAME = 'data.csv'
RECORDINGS_OUTPUT_FOLDER = 'recordings'


class AudioRecorder:
    def __init__(self):
        self.output_folder = RECORDINGS_OUTPUT_FOLDER
        self.filename = word_generator()
        self.duration = 5
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1  # Set to mono for simplicity
        self.rate = 44100
        self.is_recording = False
        self.have_data = False  # doesn't do anything for now

        self.audio = pyaudio.PyAudio()
        self.frames = []

        self.root = tk.Tk()
        self.root.title("Audio Recorder")

        # buttons
        self.buttons_canvas = tk.Frame()
        self.start_button = tk.Button(self.buttons_canvas,
                                      text="⏺️ Start Recording (1)",
                                      command=self.start_recording)
        self.start_button.grid(column=0, row=0, padx=6, pady=3)
        self.stop_button = tk.Button(self.buttons_canvas,
                                     text="⏹ Stop Recording (2)",
                                     command=self.stop_recording,
                                     state=tk.DISABLED)
        self.stop_button.grid(column=0, row=1, padx=6, pady=3)
        self.next_button = tk.Button(self.buttons_canvas,
                                     text="✔️ Save & next word (3)",
                                     command=self.save_and_next_word,
                                     state=tk.DISABLED)
        self.next_button.grid(column=1, row=0, padx=6, pady=3)
        self.skip_button = tk.Button(self.buttons_canvas,
                                     text="⛔ Skip & next word (4)",
                                     command=self.skip_word)
        self.skip_button.grid(column=1, row=1, padx=6, pady=3)

        # shortcuts for the buttons
        self.root.bind('1', lambda x: self.start_recording())
        self.root.bind('2', lambda x: self.stop_recording())
        self.root.bind('3', lambda x: self.save_and_next_word())
        self.root.bind('4', lambda x: self.skip_word())

        # lable - text being recorded
        self.word_label = tk.Label(self.buttons_canvas, text=self.filename[0],
                                   font=("Helvetica", 42))
        self.word_label.grid(column=2, row=0, rowspan=2, padx=30)

        self.buttons_canvas.pack(pady=10, padx=50, side='top', anchor='w')

        # audio wave plotter
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [])
        self.ax.set_ylim(-32768, 32768)
        self.ax.set_title('Audio Waveform')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # lable - to display current status of the recorder
        self.status_label = tk.Label(self.root, text="Let's go")
        self.status_label.pack(pady=10, padx=50, side='left')
        self.rec_location_btn = tk.Button(self.root,
                                          text='open recordings folder',
                                          command=self.open_rec_output_folder)
        self.rec_location_btn.pack(pady=10, padx=50, anchor='e')
        # handler that is excuted before closing the window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_recording(self):
        """Starts the audio recording."""
        if self.start_button['state'] == tk.DISABLED:
            return
        self.is_recording = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.skip_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.status_label['text'] = 'Recording...'
        self.frames = []
        self.record_thread = threading.Thread(target=self._record_audio)
        self.update_thread = threading.Thread(target=self.update_waveform)
        self.record_thread.start()
        self.update_thread.start()

    def stop_recording(self):
        """Stops the audio recording."""
        if self.stop_button['state'] == tk.DISABLED:
            return
        self.is_recording = False
        self.have_data = True
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.skip_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.status_label['text'] = 'Recording done, waiting for save...'

    def save_and_next_word(self):
        """ it saves the recorded audio and generates next word """
        if self.next_button['state'] == tk.DISABLED:
            return
        self.save_audio()
        self.have_data = False
        self.filename = word_generator()
        self.word_label['text'] = self.filename[0]
        self.next_button.config(state=tk.DISABLED)
        self.status_label['text'] = 'Audio saved succesfully ✔️'

    def skip_word(self):
        """ skips the a word/audio with out saving it to a file """
        if self.skip_button['state'] == tk.DISABLED:
            return
        self.filename = word_generator()
        self.word_label['text'] = self.filename[0]
        self.have_data = False
        self.next_button.config(state=tk.DISABLED)
        self.status_label['text'] = 'Word has been skipped ⚠️'

    def _record_audio(self):
        """ Handles the audio recording setup. """
        self.audio = pyaudio.PyAudio()
        stream = self.audio.open(format=self.format, channels=self.channels,
                                 rate=self.rate, input=True,
                                 frames_per_buffer=self.chunk)

        while self.is_recording:
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        self.audio.terminate()

    def update_waveform(self):
        """ Updates the waveform plot. """
        while self.is_recording:
            if not self.frames:
                # If frames are empty, wait for data to be available
                sleep(0.01)
                continue

            y = np.frombuffer(b''.join(self.frames), dtype=np.int16)
            x = np.linspace(0, len(y) / self.rate, len(y))

            window_start = max(0, len(y) - self.rate * 2)
            if window_start < len(x):
                # Ensure the x array has elements before setting limits
                self.ax.set_xlim(x[window_start], x[-1])

                self.line.set_data(x[window_start:], y[window_start:])
                self.ax.relim()
                self.ax.autoscale_view(True, True, True)
                self.canvas.draw()

    def open_rec_output_folder(self):
        """ opens the folder with the recordings """
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        webbrowser.open(os.path.join(self.output_folder, ''))

    def save_audio(self):
        """ saves the audio in the file system """
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        output_path = os.path.join(self.output_folder,
                                   self.filename[0] + ".wav")
        counter = 0
        while os.path.exists(output_path):
            output_path = os.path.join(self.output_folder,
                                       self.filename[0]+f'({counter})'+".wav")
            counter += 1
        wave_file = wave.open(output_path, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()
        update_csv(CSV_FILENAME, [self.filename[0],
                                  self.filename[1], output_path])

    def run(self):
        """ runs the tkinter """
        self.root.mainloop()

    def on_closing(self):
        """ opens a pop up message to confirm if the user wants to quit """
        self.stop_recording()
        self.root.destroy()


if __name__ == "__main__":
    if not os.path.exists(CSV_FILENAME):
        create_csv(CSV_FILENAME, CSV_HEADERS)
    recorder = AudioRecorder()
    recorder.run()
