import cv2
import numpy as np

class MotionDetector:
    def __init__(self, method='MOG2'):
        self.method = method
        if method == 'MOG2':
            self.back_sub = cv2.createBackgroundSubtractorMOG2(
                history=100,
                varThreshold=25,
                detectShadows=False
            )
        self.min_area = 500
        self.sensitivity = 0.3
        self.prev_frame = None
    
    def classify_object(self, width, height):
        if height == 0:
            return "OBJECT", (0, 255, 0)
        ratio = width / float(height)
        if ratio > 1.8:
            return "VEHICLE", (255, 0, 0)
        elif 0.5 < ratio < 1.5:
            return "HUMAN", (0, 0, 255)
        else:
            return "OBJECT", (0, 255, 0)
    
    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        if self.method == 'MOG2':
            fg_mask = self.back_sub.apply(blurred)
        else:
            if self.prev_frame is not None:
                frame_diff = cv2.absdiff(self.prev_frame, blurred)
                _, fg_mask = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
            else:
                fg_mask = np.zeros_like(blurred)
            self.prev_frame = blurred
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        annotated_frame = frame.copy()
        motion_detected = False
        classifications = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area * self.sensitivity:
                motion_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                label, color = self.classify_object(w, h)
                classifications.append(label)
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(annotated_frame, label, (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        return motion_detected, annotated_frame, fg_mask, classifications
    
    def update_sensitivity(self, value):
        self.sensitivity = value / 100.0
        print(f"Sensitivity: {self.sensitivity:.2f}")
    
    def update_min_area(self, value):
        self.min_area = value
        print(f"Min area: {value}")