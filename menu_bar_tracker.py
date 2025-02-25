import shlex
import subprocess
import json
import time
from datetime import datetime
from Cocoa import (
    NSApplication, NSApp, NSObject, NSMenu, NSMenuItem, NSStatusBar, NSStatusItem, NSImage, NSTimer
)

# 🔹 Use absolute paths to ensure subprocess works correctly
TRACK_SCRIPT = "/Users/loganhenson/Desktop/track/track.py"
PYTHON_EXEC = "/Users/loganhenson/Desktop/track/.venv/bin/python"

class TimeTrackerMenuApp(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        """Initialize menu bar app and periodically check status"""
        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)  # Use -1 for dynamic width

        # Create the menu
        self.menu = NSMenu()
        self.menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit", "quitApp:", "q"))
        self.statusItem.setMenu_(self.menu)

        self.is_tracking = False
        self.current_task = None
        self.start_time = None
        self.updateMenuBarIcon()

        # Schedule periodic updates every 1 second to show real-time seconds
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0, self, "updateTrackingState", None, True
        )

    def applicationSupportsSecureRestorableState_(self, app):
        """Fix macOS secure coding warning"""
        return True

    def get_tracking_state(self):
        """Fetch tracking status from CLI using the full path, safely handling spaces"""
        try:
            # 🔹 Ensure paths with spaces are safely quoted
            command = f"{shlex.quote(PYTHON_EXEC)} {shlex.quote(TRACK_SCRIPT)} --status"
            output = subprocess.check_output(command, shell=True)
            state = json.loads(output.decode("utf-8"))
            return state
        except Exception as e:
            print("Error fetching tracking state:", e)
            return {"tracking": False, "current_task": None, "start_time": None}

    def calculate_elapsed_time(self, start_time):
        """Calculate elapsed time since tracking started, including seconds"""
        if start_time is None:
            return "0s"

        elapsed = int(time.time() - start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def updateTrackingState(self):
        """Fetch state from CLI and update UI accordingly"""
        state = self.get_tracking_state()

        self.is_tracking = state.get("tracking", False)
        self.current_task = state.get("current_task", None)
        self.start_time = state.get("start_time", None)

        self.updateMenuBarIcon()

    # 🔹 Limit task name to 20 characters
    def truncate_task_name(self, task_name, max_length=9):
        return (task_name[:max_length] + "...") if len(task_name) > max_length else task_name

    # 🔹 Shorten time format (e.g., "1:23:45")
    def format_compact_time(self, start_time):
        if start_time is None:
            return "0:00"

        elapsed = int(time.time() - start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}:{minutes:02}:{seconds:02}"
        return f"{minutes}:{seconds:02}"

    def updateMenuBarIcon(self):
        """Update the menu bar icon and text based on tracking state"""
        now = datetime.now()
        is_work_hours = 8 <= now.hour < 17  # Work hours: 8 AM - 5 PM

        if self.is_tracking:
            icon_name = "NSStatusAvailable"  # ✅ Green dot (Tracking)
            elapsed_time = self.format_compact_time(self.start_time)
            task_display = self.truncate_task_name(self.current_task)
            title = f"{task_display} ⏳ {elapsed_time}"
        elif is_work_hours:
            icon_name = "NSStatusUnavailable"  # 🔴 Red dot (Idle during work hours)
            title = "⚠️ Not Tracking!"
        else:
            icon_name = "NSStatusNone"  # Still show tracking outside work hours
            title = "Off the clock"

        # Set the menu bar icon
        icon = NSImage.imageNamed_(icon_name)
        if icon:
            self.statusItem.button().setImage_(icon)

        self.statusItem.button().setTitle_(title)

    def quitApp_(self, sender):
        """Quit the application"""
        NSApp.terminate_(self)

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = TimeTrackerMenuApp.alloc().init()
    app.setDelegate_(delegate)
    app.run()
