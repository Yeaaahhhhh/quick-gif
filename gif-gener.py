import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import os
import threading
from PIL import ImageGrab

class ScreenRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Recorder")
        self.is_recording = False
        self.is_paused = False
        self.start_time = None
        self.recorded_time = 0

        self.select_area_btn = tk.Button(self.root, text="Select Area", command=self.select_area)
        self.select_area_btn.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Status: Not Recording")
        self.status_label.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def select_area(self):
        self.root.iconify()
        time.sleep(1)
        self.top = tk.Toplevel(self.root)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-alpha", 0.3)
        self.top.attributes("-topmost", True)
        self.top.bind("<ButtonPress-1>", self.on_rect_start)
        self.top.bind("<B1-Motion>", self.on_rect_move)
        self.top.bind("<ButtonRelease-1>", self.on_rect_end)
        self.root.wait_window(self.top)

    def on_rect_start(self, event):
        self.start_x = self.top.winfo_pointerx() - self.top.winfo_rootx()
        self.start_y = self.top.winfo_pointery() - self.top.winfo_rooty()
        self.rect = self.top.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_rect_move(self, event):
        x = self.top.winfo_pointerx() - self.top.winfo_rootx()
        y = self.top.winfo_pointery() - self.top.winfo_rooty()
        self.top.coords(self.rect, self.start_x, self.start_y, x, y)

    def on_rect_end(self, event):
        self.area = (self.start_x, self.start_y, self.top.winfo_pointerx() - self.top.winfo_rootx(), self.top.winfo_pointery() - self.top.winfo_rooty())
        self.top.destroy()
        self.root.deiconify()

        if self.area:
            self.start_recording()

    def start_recording(self):
        self.frames = []
        self.is_recording = True
        self.start_time = time.time()

        self.status_label.config(text="Status: Recording")
        self.record_thread = threading.Thread(target=self.record)
        self.record_thread.start()

        self.pause_btn = tk.Button(self.root, text="⏸", command=self.pause_recording)
        self.pause_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(self.root, text="⏹", command=self.stop_recording)
        self.stop_btn.pack(side=tk.RIGHT, padx=10)

    def record(self):
        while self.is_recording:
            if not self.is_paused:
                frame = ImageGrab.grab(bbox=self.area)
                self.frames.append(frame)
            time.sleep(1/60) # Changed to 1/24 for a minimum of 24 FPS

    def pause_recording(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.config(text="⏸")
            self.status_label.config(text="Status: Recording")
        else:
            self.is_paused = True
            self.pause_btn.config(text="▶")
            self.status_label.config(text="Status: Paused")

    def stop_recording(self):
        self.is_recording = False
        self.record_thread.join()

        duration = round(time.time() - self.start_time, 2)
        self.status_label.config(text=f"Status: Not Recording (Last recording: {duration}s)")

        self.save_gif(duration)

        self.pause_btn.destroy()
        self.stop_btn.destroy()

    def save_gif(self, duration):
        gif_filename = f"screen_recording_{int(time.time())}.gif"
        self.frames[0].save(gif_filename, save_all=True, append_images=self.frames[1:], duration=int(1000/24), loop=0)
        file_size = round(os.path.getsize(gif_filename) / 1024, 2)

        messagebox.showinfo("Recording Saved", f"Recording saved as {gif_filename}.\nFile size: {file_size} KB\nDuration: {duration}s")

    def on_close(self):
        if self.is_recording:
            if messagebox.askokcancel("Quit", "Recording is in progress. Do you want to stop recording and exit?"):
                self.stop_recording()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    recorder = ScreenRecorder()