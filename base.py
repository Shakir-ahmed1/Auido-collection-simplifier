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
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np
from time import sleep
import webbrowser
from tkinter import filedialog
from utils import word_generator, update_csv, dataset_count
from utils import OUTPUT_DATASET_FILENAME
RECORDINGS_OUTPUT_FOLDER = 'recordings'


class AudioRecorder:
    def __init__(self):
        self.filename = word_generator()
        self.duration = 5
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1  # Set to mono for simplicity
        self.rate = 44100
        self.is_recording = False
        self.is_replaying = False
        self.have_data = False  # doesn't do anything for now

        self.audio = pyaudio.PyAudio()
        self.frames = []

        self.root = tk.Tk()
        self.root.title("Audio Recorder")

        # buttons
        self.buttons_canvas = tk.Frame()
        self.start_button = tk.Button(self.buttons_canvas, text="⏺️ Start Recording (1)",
                                      command=self.start_recording)
        self.start_button.grid(column=0, row=0, padx=3, pady=3)
        self.stop_button = tk.Button(self.buttons_canvas, text="⏹ Stop Recording (2)",
                                     command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.grid(column=0, row=1, padx=3, pady=3)
        self.next_button = tk.Button(self.buttons_canvas, text="✔️ Save & next word (3)",
                                     command=self.save_and_next_word, state=tk.DISABLED)
        self.next_button.grid(column=1, row=0, padx=3, pady=3)
        self.skip_button = tk.Button(self.buttons_canvas, text="⛔ Skip & next word (4)",
                                     command=self.skip_word)
        self.skip_button.grid(column=1, row=1, padx=3, pady=3)
        self.replay_button = tk.Button(self.buttons_canvas, text="🔁 Replay Recording (5)",
                                       command=self.replay_audio, state=tk.DISABLED,
                                       background='#FF9999')
        self.replay_button.grid(column=0, row=2, padx=3, pady=3)

        self.stop_reply_button = tk.Button(self.buttons_canvas, text="⏹ Stop replaying (6)",
                                           command=self.stop_replaying, state=tk.DISABLED,
                                           background='#FF9999')
        self.stop_reply_button.grid(column=1, row=2, padx=3, pady=3)

        # lable - text being recorded
        self.word_label = tk.Label(self.buttons_canvas, text=self.filename[0],
                                   font=("Helvetica", 20))
        self.word_label.grid(column=2, row=0, rowspan=1, padx=30, sticky='w')
        self.definition_label = tk.Label(self.buttons_canvas, text=self.filename[1])
        self.definition_label.grid(column=2, row=1, padx=30, sticky='w')

        self.buttons_canvas.pack(pady=10, padx=50, side='top', anchor='w')

        # audio wave plotter
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0, right=1)
        self.line, = self.ax.plot([], [])
        self.line.set_color('blue')
        self.ax.set_ylim(-32768, 32768)
        self.ax.yaxis.set_visible(False)
        self.ax.set_title('Audio Waveform')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().config(height=200)
        self.canvas.get_tk_widget().pack()

        # lable - to display current status of the recorder
        self.status_label = tk.Label(self.root, text="Let's go")
        self.status_label.pack(pady=10, padx=50, side='left')
        self.rec_location_btn = tk.Button(self.root,
                                          text='open recordings folder',
                                          command=self.open_rec_output_folder)
        self.rec_location_btn.pack(pady=10, padx=50, anchor='e')
        # handler that is excuted before closing the window
        dialog_title = 'select the output folder for the datataset'
        self.output_folder = filedialog.askdirectory(title=dialog_title)
        self.root.focus_force()

        self.dataset_count_lable = tk.Label(self.buttons_canvas,
                                            text=dataset_count(
                                                   os.path.join(self.output_folder,
                                                                OUTPUT_DATASET_FILENAME)))
        self.dataset_count_lable.grid(column=2, row=2, padx=30, sticky='w')

        # shortcuts for the buttons
        self.root.bind('1', lambda x: self.start_recording())
        self.root.bind('2', lambda x: self.stop_recording())
        self.root.bind('3', lambda x: self.save_and_next_word())
        self.root.bind('4', lambda x: self.skip_word())
        self.root.bind('5', lambda x: self.replay_audio())
        self.root.bind('6', lambda x: self.stop_replaying())
        self.root.bind('7', lambda x: self.open_rec_output_folder())

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_recording(self):
        """Starts the audio recording."""
        if self.start_button['state'] == tk.DISABLED:
            return
        self.is_recording = True
        self.line.set_color('blue')
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.skip_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.replay_button.config(state=tk.DISABLED)  # Disable replay button
        self.status_label['text'] = 'Recording...'
        self.frames = []
        self.record_thread = threading.Thread(target=self._record_audio)
        self.update_thread = threading.Thread(target=self.update_waveform)
        self.record_thread.start()
        self.update_thread.start()

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
        self.replay_button.config(state=tk.NORMAL)  # Enable replay button
        self.status_label['text'] = 'Recording done, waiting for save...'

    def save_and_next_word(self):
        """ it saves the recorded audio and generates next word """
        if self.next_button['state'] == tk.DISABLED:
            return
        self.save_audio()
        self.have_data = False
        self.filename = word_generator()
        self.word_label['text'] = self.filename[0]
        self.definition_label['text'] = self.filename[1]
        self.dataset_count_lable['text'] = dataset_count(
                                    os.path.join(self.output_folder,
                                                 OUTPUT_DATASET_FILENAME))
        self.next_button.config(state=tk.DISABLED)
        self.replay_button.config(state=tk.DISABLED)
        self.status_label['text'] = 'Audio saved succesfully ✔️'

    def skip_word(self):
        """ skips the a word/audio with out saving it to a file """
        if self.skip_button['state'] == tk.DISABLED:
            return
        self.filename = word_generator()
        self.word_label['text'] = self.filename[0]
        self.definition_label['text'] = self.filename[1]
        self.have_data = False
        self.next_button.config(state=tk.DISABLED)
        self.replay_button.config(state=tk.DISABLED)
        self.status_label['text'] = 'Word has been skipped ⚠️'

    def replay_audio(self):
        """ replays the recorded audio """
        if self.replay_button['state'] == tk.DISABLED:
            return
        self.status_label['text'] = 'Replaying...'
        self.stop_reply_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.skip_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.replay_button.config(state=tk.DISABLED)
        self.is_replaying = True
        self.play_thread = threading.Thread(target=self._replay_audio)
        self.update_thread = threading.Thread(target=self.update_waveform_playback)
        self.play_thread.start()
        self.update_thread.start()

    def _replay_audio(self):
        """Replays the recorded audio."""
        self.line.set_color('red')
        self.output_frames = []
        # Open a new audio stream for playback
        stream = self.audio.open(format=self.format, channels=self.channels,
                                 rate=self.rate, output=True)
        for frame in self.frames:
            stream.write(frame)
            self.output_frames.append(frame)
            if not self.is_replaying:
                break
        stream.stop_stream()
        stream.close()
        self.stop_replaying()

    def update_waveform_playback(self):
        """ Updates the waveform plot during playback. """
        while self.is_replaying:
            y = np.frombuffer(b''.join(self.output_frames), dtype=np.int16)
            x = np.linspace(0, len(y) / self.rate, len(y))

            window_start = max(0, len(y) - self.rate * 2)
            if window_start < len(x):
                # Ensure the x array has elements before setting limits
                self.ax.set_xlim(x[window_start], x[-1])

                self.line.set_data(x[window_start:], y[window_start:])
                self.ax.relim()
                self.ax.autoscale_view(True, True, True)
                self.canvas.draw()

    def stop_replaying(self):
        """ stops the audio playing """
        if self.stop_reply_button['state'] == tk.DISABLED:
            return
        self.is_replaying = False
        self.stop_reply_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.skip_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.replay_button.config(state=tk.NORMAL)

    def open_rec_output_folder(self):
        """ opens the folder with the recordings """
        rec_path = os.path.join(self.output_folder, 'recordings')
        if not os.path.exists(rec_path):
            os.makedirs(rec_path)
        webbrowser.open(rec_path)

    def save_audio(self):
        """ saves the audio in the file system """
        rec_path = os.path.join(self.output_folder, 'recordings')
        if not os.path.exists(rec_path):
            os.makedirs(rec_path)

        output_path = os.path.join(rec_path,
                                   self.filename[0].replace('/', '') + ".wav")
        counter = 0
        while os.path.exists(output_path):
            output_path = os.path.join(self.output_folder,
                                       self.filename[0]
                                       .replace('/', '') +
                                       f'({counter})'+".wav")
            counter += 1
        wave_file = wave.open(output_path, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()
        update_csv(os.path.join(self.output_folder, OUTPUT_DATASET_FILENAME), [self.filename[0],
                   self.filename[1], output_path.lstrip(self.output_folder)
                                                .lstrip('/').lstrip(r"\\")])

    def run(self):
        """ runs the tkinter """
        self.root.mainloop()

    def on_closing(self):
        """ opens a pop up message to confirm if the user wants to quit """
        self.stop_recording()
        self.stop_replaying()
        result = messagebox.askyesno("Exit Application",
                                     "Do you really want to exit?")
        if result:
            self.root.quit()


if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.run()
