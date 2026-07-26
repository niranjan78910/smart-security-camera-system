import os
from datetime import datetime

class EventLogger:
    def __init__(self):
        self.log_dir = "../logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.log_file = os.path.join(self.log_dir, "security_events.txt")
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("WAREHOUSE SECURITY CAMERA EVENT LOG\n")
                f.write("=" * 60 + "\n")
                f.write("Time                | Event Type     | Duration | Video\n")
                f.write("-" * 60 + "\n")
    
    def log_event(self, event_type, video_file="", duration=0):
        try:
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"{time_now} | {event_type:16} | {duration:5.1f}s | {video_file}\n"
            with open(self.log_file, 'a') as f:
                f.write(log_line)
            print("\n" + "~" * 40)
            print("EVENT LOGGED")
            print("~" * 40)
            print(f"Time: {time_now}")
            print(f"Event: {event_type}")
            print(f"Duration: {duration:.1f}s")
            print("~" * 40)
            return True
        except Exception as e:
            print(f"Log error: {e}")
            return False
    
    def get_recent_events(self, count=5):
        events = []
        if not os.path.exists(self.log_file):
            return events
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            for line in lines[4:]:
                line = line.strip()
                if line and not line.startswith(("-", "=")):
                    events.append(line)
            if events:
                return events[-count:]
            else:
                return []
        except Exception as e:
            print(f"Read error: {e}")
            return []