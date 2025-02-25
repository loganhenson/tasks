import subprocess
import json
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
        self.updateMenuBarIcon()

        # Schedule periodic updates every 5 seconds
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            5.0, self, "updateTrackingState", None, True
        )

    def applicationSupportsSecureRestorableState_(self, app):
        """Fix macOS secure coding warning"""
        return True

    def get_tracking_state(self):
        """Fetch tracking status from CLI using the full path"""
        try:
            output = subprocess.check_output([PYTHON_EXEC, TRACK_SCRIPT, "--status"])
            return json.loads(output.decode("utf-8"))
        except Exception as e:
            print("Error fetching tracking state:", e)
            return {"tracking": False, "current_task": None}

    def updateTrackingState(self):
        """Fetch state from CLI and update UI accordingly"""
        state = self.get_tracking_state()

        self.is_tracking = state.get("tracking", False)
        self.current_task = state.get("current_task", None)

        self.updateMenuBarIcon()

    def updateMenuBarIcon(self):
        """Update the menu bar icon and text based on tracking state"""
        now = datetime.now()
        is_work_hours = 8 <= now.hour < 17  # Work hours: 8 AM - 5 PM

        if self.is_tracking:
            icon_name = "NSStatusAvailable"
            title = self.current_task
        elif is_work_hours:
            icon_name = "NSStatusUnavailable"
            title = "⚠️ Not Tracking!"
        else:
            icon_name = "NSStatusNone"
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
