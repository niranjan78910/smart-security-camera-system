import cv2
import os

class VideoProcessor:
    @staticmethod
    def save_event_video(frames, filename, fps=30):
        if len(frames) == 0:
            print("No frames")
            return False
        try:
            height, width = frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
            if not out.isOpened():
                print(f"Cant create: {filename}")
                return False
            for frame in frames:
                out.write(frame)
            out.release()
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print(f"Video saved: {filename}")
                return True
            else:
                print(f"File problem: {filename}")
                return False
        except Exception as e:
            print(f"Save video error: {e}")
            return False
    
    @staticmethod
    def get_video_info(filename):
        if not os.path.exists(filename):
            print(f"Missing: {filename}")
            return None
        try:
            cap = cv2.VideoCapture(filename)
            if not cap.isOpened():
                return None
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if fps > 0:
                duration = frame_count / fps
            else:
                duration = 0
            cap.release()
            return {
                'filename': os.path.basename(filename),
                'width': width,
                'height': height,
                'fps': fps,
                'frames': frame_count,
                'duration': f"{duration:.1f} seconds",
                'resolution': f"{width}x{height}"
            }
        except Exception as e:
            print(f"Video info error: {e}")
            return None
    
    @staticmethod
    def save_screenshot(frame, filename):
        try:
            cv2.imwrite(filename, frame)
            if os.path.exists(filename):
                print(f"Screenshot: {filename}")
                return True
            else:
                print(f"No screenshot: {filename}")
                return False
        except Exception as e:
            print(f"Screenshot error: {e}")
            return False