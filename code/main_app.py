import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import queue
import time
import os
from datetime import datetime
from collections import Counter

from motion_detector import MotionDetector
from video_processor import VideoProcessor
from event_logger import EventLogger

print("=" * 60)
print("SMART SECURITY CAMERA SYSTEM")
print("CSY3058 Assignment")
print("=" * 60)

class SecurityCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Security Camera")
        self.root.geometry("1100x750")
        self.motion_detector = MotionDetector(method='MOG2')
        self.video_processor = VideoProcessor()
        self.event_logger = EventLogger()
        self.is_playing = False
        self.is_recording = False
        self.video_source = 0
        self.cap = None
        self.event_count = 0
        self.event_frames = []
        self.last_classifications = []
        self.video_queue = queue.Queue(maxsize=10)
        self.setup_gui()
        self.update_status("Ready. Click START.")
        self.update_status_bar()
    
    def setup_gui(self):
        main_container = tk.Frame(self.root, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        video_frame = tk.LabelFrame(main_container, text="LIVE CAMERA", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.video_label = tk.Label(video_frame, bg='black', relief=tk.SUNKEN)
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.video_info = tk.Label(video_frame, text="Status: Ready | Source: Webcam", 
                                  font=("Arial", 10), fg="blue", bg="#f0f0f0")
        self.video_info.pack(pady=5)
        control_frame = tk.Frame(main_container, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, pady=10)
        left_controls = tk.Frame(control_frame, bg="#f0f0f0")
        left_controls.pack(side=tk.LEFT, padx=20)
        button_frame = tk.Frame(left_controls, bg="#f0f0f0")
        button_frame.pack(anchor=tk.W, pady=5)
        btn_style = {'width': 12, 'height': 1, 'font': ("Arial", 10, "bold")}
        self.start_btn = tk.Button(button_frame, text="▶ START", 
                                  command=self.start_video, bg="#4CAF50", fg="white",
                                  **btn_style)
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.stop_btn = tk.Button(button_frame, text="⏹ STOP", 
                                 command=self.stop_video, bg="#f44336", fg="white",
                                 state=tk.DISABLED, **btn_style)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.record_btn = tk.Button(button_frame, text="● RECORD", 
                                   command=self.toggle_recording, bg="#607d8b", fg="white",
                                   state=tk.DISABLED, **btn_style)
        self.record_btn.pack(side=tk.LEFT, padx=5, pady=5)
        middle_controls = tk.Frame(control_frame, bg="#f0f0f0")
        middle_controls.pack(side=tk.LEFT, padx=40)
        sens_frame = tk.Frame(middle_controls, bg="#f0f0f0")
        sens_frame.pack(pady=5)
        tk.Label(sens_frame, text="SENSITIVITY:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        self.sensitivity_var = tk.IntVar(value=50)
        self.sensitivity_scale = tk.Scale(sens_frame, from_=1, to=100, 
                                         orient=tk.HORIZONTAL, 
                                         variable=self.sensitivity_var,
                                         length=200, showvalue=True,
                                         command=self.update_sensitivity,
                                         bg="#f0f0f0", highlightbackground="#f0f0f0")
        self.sensitivity_scale.pack(side=tk.LEFT, padx=10)
        legend_frame = tk.Frame(middle_controls, bg="#f0f0f0")
        legend_frame.pack(pady=5)
        tk.Label(legend_frame, text="CLASSIFICATION:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        colors_frame = tk.Frame(legend_frame, bg="#f0f0f0")
        colors_frame.pack(side=tk.LEFT, padx=10)
        human_frame = tk.Frame(colors_frame, bg="#f0f0f0")
        human_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(human_frame, text="●", fg="red", font=("Arial", 14), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Label(human_frame, text="HUMAN", font=("Arial", 9), 
                bg="#f0f0f0").pack(side=tk.LEFT, padx=2)
        vehicle_frame = tk.Frame(colors_frame, bg="#f0f0f0")
        vehicle_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(vehicle_frame, text="●", fg="blue", font=("Arial", 14), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Label(vehicle_frame, text="VEHICLE", font=("Arial", 9), 
                bg="#f0f0f0").pack(side=tk.LEFT, padx=2)
        object_frame = tk.Frame(colors_frame, bg="#f0f0f0")
        object_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(object_frame, text="●", fg="green", font=("Arial", 14), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Label(object_frame, text="OBJECT", font=("Arial", 9), 
                bg="#f0f0f0").pack(side=tk.LEFT, padx=2)
        right_controls = tk.Frame(control_frame, bg="#f0f0f0")
        right_controls.pack(side=tk.RIGHT, padx=20)
        stats_frame = tk.Frame(right_controls, bg="#f0f0f0")
        stats_frame.pack(pady=5)
        self.stats_label = tk.Label(stats_frame, 
                                   text="Events: 0 | Status: Ready",
                                   font=("Arial", 10, "bold"), 
                                   fg="#333333", bg="#f0f0f0")
        self.stats_label.pack()
        log_frame = tk.LabelFrame(main_container, text="EVENTS LOG", 
                                 font=("Arial", 12, "bold"), bg="#f0f0f0")
        log_frame.pack(fill=tk.BOTH, expand=True)
        listbox_frame = tk.Frame(log_frame, bg="white")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.events_listbox = tk.Listbox(listbox_frame, 
                                        yscrollcommand=scrollbar.set,
                                        font=("Courier", 10),
                                        height=8,
                                        bg="white",
                                        selectbackground="#e0e0e0")
        self.events_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.events_listbox.yview)
        self.event_count_label = tk.Label(log_frame, 
                                         text="Total Events: 0", 
                                         font=("Arial", 10, "bold"),
                                         bg="#f0f0f0",
                                         fg="#333333")
        self.event_count_label.pack(anchor=tk.W, padx=10, pady=5)
        self.status_bar = tk.Label(self.root, text="System Ready | v1.0", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  font=("Arial", 10), bg="#e0e0e0", fg="#333333")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def start_video(self):
        if self.is_playing:
            return
        try:
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Camera not found!")
                return
            self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.video_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            if self.video_fps <= 0:
                self.video_fps = 30
            info_text = f"Resolution: {self.video_width}x{self.video_height} | FPS: {self.video_fps}"
            self.video_info.config(text=info_text)
            self.is_playing = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.record_btn.config(state=tk.NORMAL)
            self.processing_thread = threading.Thread(target=self.process_video, daemon=True)
            self.processing_thread.start()
            self.update_display()
            self.update_status("Camera active")
        except Exception as e:
            messagebox.showerror("Error", f"Start failed: {str(e)}")
    
    def process_video(self):
        while self.is_playing and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                break
            motion_detected, annotated_frame, motion_mask, classifications = self.motion_detector.detect(frame)
            if classifications:
                self.last_classifications = classifications
            if motion_detected and self.is_recording:
                self.event_frames.append(annotated_frame.copy())
                max_buffer = self.video_fps * 5
                if len(self.event_frames) > max_buffer:
                    self.event_frames = self.event_frames[-max_buffer:]
                if len(self.event_frames) >= self.video_fps * 2:
                    self.save_event()
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            display_height = 500
            display_width = int(self.video_width * (display_height / self.video_height))
            resized_frame = cv2.resize(rgb_frame, (display_width, display_height))
            img = Image.fromarray(resized_frame)
            photo = ImageTk.PhotoImage(image=img)
            try:
                self.video_queue.put(photo, block=False)
            except queue.Full:
                pass
            time.sleep(1.0 / self.video_fps)
    
    def update_display(self):
        try:
            if not self.video_queue.empty():
                photo = self.video_queue.get_nowait()
                self.video_label.config(image=photo)
                self.video_label.image = photo
        except queue.Empty:
            pass
        if self.is_playing:
            self.root.after(30, self.update_display)
    
    def stop_video(self):
        self.is_playing = False
        self.is_recording = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.record_btn.config(state=tk.DISABLED, bg="#607d8b", text="● RECORD")
        self.video_label.config(image='')
        self.update_status("Stopped")
    
    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_btn.config(bg="#d32f2f", text="◼ RECORDING")
            self.update_status("Recording ON")
            if not os.path.exists("../events"):
                os.makedirs("../events")
                print("Made events folder")
        else:
            self.record_btn.config(bg="#607d8b", text="● RECORD")
            self.update_status("Recording OFF")
    
    def save_event(self):
        if len(self.event_frames) < self.video_fps:
            return
        print("\n" + "=" * 60)
        print("SAVING EVENT")
        print("=" * 60)
        if self.last_classifications:
            counter = Counter(self.last_classifications)
            main_class = counter.most_common(1)[0][0]
            event_type = f"{main_class} DETECTED"
            print(f"Class: {main_class}")
        else:
            event_type = "MOTION DETECTED"
            print("Class: Unknown")
        if not os.path.exists("../events"):
            os.makedirs("../events")
            print("Made events folder")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../events/{event_type.replace(' ', '_')}_{self.event_count:03d}_{timestamp}.avi"
        print(f"Saving: {filename}")
        print(f"Frames: {len(self.event_frames)}")
        try:
            height, width = self.event_frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(filename, fourcc, self.video_fps, (width, height))
            for frame in self.event_frames:
                out.write(frame)
            out.release()
            print("Video saved")
            screenshot_file = filename.replace('.avi', '.jpg')
            cv2.imwrite(screenshot_file, self.event_frames[-1])
            print(f"Screenshot: {screenshot_file}")
            duration = len(self.event_frames) / float(self.video_fps)
            success = self.event_logger.log_event(
                event_type=event_type,
                video_file=filename,
                duration=duration
            )
            if success:
                short_time = timestamp[8:]
                event_text = f"{short_time} - {event_type} ({duration:.1f}s)"
                self.events_listbox.insert(tk.END, event_text)
                self.events_listbox.yview(tk.END)
                self.event_count += 1
                self.event_count_label.config(text=f"Total Events: {self.event_count}")
                print(f"Event #{self.event_count} logged")
            self.event_frames = []
            self.last_classifications = []
        except Exception as e:
            print(f"Save error: {e}")
    
    def update_sensitivity(self, value):
        self.motion_detector.update_sensitivity(int(value))
        self.update_status(f"Sensitivity: {value}%")
    
    def update_status(self, message):
        self.status_bar.config(text=f"Status: {message}")
        print(f"[STATUS] {message}")
    
    def update_status_bar(self):
        if self.is_playing:
            status = f"Monitoring | Events: {self.event_count}"
            if self.is_recording:
                status += " | ⚫ RECORDING"
            self.stats_label.config(text=status)
        self.root.after(1000, self.update_status_bar)

def main():
    root = tk.Tk()
    app = SecurityCameraApp(root)
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.mainloop()

if __name__ == "__main__":
    main()