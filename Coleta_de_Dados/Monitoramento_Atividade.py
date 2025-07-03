import psutil
import time
import datetime
import json
import pygetwindow as gw # You might need to install this: pip install pygetwindow

# --- Configuration ---
RECORD_INTERVAL_SECONDS = 5 # How often to check for activity
OUTPUT_FILE = "activity_log.json"

# --- Data Structure ---
activity_log = []
current_active_window = None
session_start_time = None

# --- Helper Functions ---

def get_active_application_info():
    """
    Attempts to get the name of the active application and window title.
    This can be tricky and might vary by OS.
    """
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            app_name = active_window.title # Often includes app name or URL
            return app_name
    except Exception as e:
        # print(f"Error getting active window: {e}")
        return None
    return None

def save_log():
    """Saves the activity log to a JSON file."""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(activity_log, f, indent=4, ensure_ascii=False)
    print(f"Log saved to {OUTPUT_FILE}")

# --- Main Logic ---

print("Starting activity tracking. Press Ctrl+C to stop.")

try:
    while True:
        timestamp = datetime.datetime.now().isoformat()
        current_app_info = get_active_application_info()

        if current_app_info != current_active_window:
            # New active window/application
            if current_active_window is not None and session_start_time is not None:
                # Log the previous session
                duration_seconds = (datetime.datetime.now() - session_start_time).total_seconds()
                activity_log.append({
                    "timestamp_end": timestamp,
                    "application_or_url": current_active_window,
                    "duration_seconds": round(duration_seconds, 2)
                })
                print(f"Logged: {current_active_window} for {round(duration_seconds, 2)} seconds")
                save_log() # Save every time an activity changes

            # Start new session
            current_active_window = current_app_info
            session_start_time = datetime.datetime.now()
            print(f"Active now: {current_active_window} at {timestamp}")
        
        # If the window is still the same, screen is still in use for this app
        # The duration will be calculated when the window changes

        time.sleep(RECORD_INTERVAL_SECONDS)

except KeyboardInterrupt:
    # On Ctrl+C, log the final active session
    if current_active_window is not None and session_start_time is not None:
        duration_seconds = (datetime.datetime.now() - session_start_time).total_seconds()
        activity_log.append({
            "timestamp_end": datetime.datetime.now().isoformat(),
            "application_or_url": current_active_window,
            "duration_seconds": round(duration_seconds, 2)
        })
        print(f"Logged final session: {current_active_window} for {round(duration_seconds, 2)} seconds")
    
    save_log()
    print("Activity tracking stopped.")
    