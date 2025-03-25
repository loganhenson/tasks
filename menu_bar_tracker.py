import os
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

    def get_today_tasks(self, today_key):
        """Fetch today's logged tasks from ~/track.json and format time correctly"""
        track_file = os.path.expanduser("~/track.json")

        if not os.path.exists(track_file):
            return {}

        with open(track_file, "r") as f:
            data = json.load(f)

        # 🔹 Convert seconds into HH:MM:SS format
        tasks = data.get(today_key, {})
        formatted_tasks = {task: self.format_compact_time(duration) for task, duration in tasks.items()}

        return formatted_tasks  # Return formatted task times

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
    def truncate_task_name(self, task_name, max_length=3):
        return (task_name[:max_length] + "...") if len(task_name) > max_length else task_name

    # 🔹 Shorten time format (e.g., "1:23:45")
    def format_compact_time(self, total_seconds):
        """Format elapsed time or total logged time to HH:MM:SS"""
        if total_seconds is None or total_seconds <= 0:
            return "0:00"

        elapsed = int(total_seconds)  # Ensure it's an integer
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}:{minutes:02}:{seconds:02}"
        return f"{minutes}:{seconds:02}"

    def updateMenuBarIcon(self):
        """Update the menu bar icon and add tracking + today's tasks to the dropdown menu"""
        now = datetime.now()
        today_key = now.strftime("%Y-%m-%d")  # Get today's date
        is_work_hours = 8 <= now.hour < 17  # Work hours: 8 AM - 5 PM

        # 🔹 Set icon based on tracking state
        if self.is_tracking:
            icon_name = "NSStatusAvailable"  # ✅ Green dot (Tracking)
            elapsed_time = self.format_compact_time(time.time() - self.start_time)  # ✅ Use elapsed time here!
            title = f"⏳ {elapsed_time}"  # ⏳ 1:23:45
        elif is_work_hours:
            icon_name = "NSStatusUnavailable"  # 🔴 Red dot (Idle during work hours)
            title = "⚠️"
        else:
            icon_name = "NSStatusNone"  # ⚫ Gray dot (Off the clock)
            title = "⚫"

        # Set the menu bar icon
        icon = NSImage.imageNamed_(icon_name)
        if icon:
            self.statusItem.button().setImage_(icon)

        self.statusItem.button().setTitle_(title)  # ⏳ 1:23:45 in menu bar

        # 🔹 Update dropdown menu (clear first)
        self.menu.removeAllItems()

        # Add the currently tracked task
        if self.is_tracking:
            task_display = self.truncate_task_name(self.current_task, max_length=40)
            tracking_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Tracking: {task_display} ⏳ {elapsed_time}", None, ""
            )
            tracking_item.setEnabled_(False)  # Non-clickable text item
            self.menu.addItem_(tracking_item)
            self.menu.addItem_(NSMenuItem.separatorItem())  # Separator

        # 🔹 Show today's logged tasks from `~/track.json`
        tasks_today = self.get_today_tasks(today_key)

        if tasks_today:
            for task, formatted_time in tasks_today.items():
                if task != self.current_task:  # ✅ Don't duplicate currently tracked task
                    task_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                        f"{task} ⏳ {formatted_time}", None, ""
                    )
                    task_item.setEnabled_(False)
                    self.menu.addItem_(task_item)

        # 🔹 Add a Quit option at the bottom
        self.menu.addItem_(NSMenuItem.separatorItem())  # Separator
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "quitApp:", "q"
        )
        self.menu.addItem_(quit_item)

        # 🔹 Update the menu
        self.statusItem.setMenu_(self.menu)

    def quitApp_(self, sender):
        """Quit the application"""
        NSApp.terminate_(self)

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = TimeTrackerMenuApp.alloc().init()
    app.setDelegate_(delegate)
    app.run()
