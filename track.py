#!/usr/bin/env python3
import json
import os
import subprocess
import time
import argparse
import signal
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live

TRACK_FILE = os.path.expanduser("~/track.json")
ACTIVE_TASK_FILE = os.path.expanduser("~/track_active.json")
console = Console()

def load_json():
    """Load track.json or return an empty dictionary."""
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return json.load(f)
    return {}

def save_json(data):
    """Save track.json"""
    with open(TRACK_FILE, "w") as f:
        json.dump(data, f, indent=4)

def list_tasks():
    """Display today's tracked tasks and total duration."""
    data = load_json()
    today_key = datetime.now().strftime("%Y-%m-%d")
    today_tasks = data.get(today_key, {})

    if not today_tasks:
        console.print("[yellow]No tasks tracked today.[/yellow]")
        return

    table = Table(title=f"📅 Tracked Tasks for {today_key}", show_lines=True)
    table.add_column("Task", style="bold magenta")
    table.add_column("Duration", justify="right", style="bold green")

    total_duration = 0
    for task, duration in today_tasks.items():
        total_duration += duration
        table.add_row(task, format_time(duration))

    table.add_row("[bold]Total[/bold]", f"[bold green]{format_time(total_duration)}[/bold green]")
    console.print(table)
def track_task(title, start_offset):
    """Track a task and update ~/track.json upon Ctrl+C."""
    start_time = time.time() - start_offset
    today_key = datetime.now().strftime("%Y-%m-%d")

    # Save active task to a separate file
    active_task = {"tracking": True, "current_task": title, "start_time": start_time}
    with open(ACTIVE_TASK_FILE, "w") as f:
        json.dump(active_task, f)

    def handle_exit(signum, frame):
        """Handle Ctrl+C and save tracked time."""
        end_time = time.time()
        duration = int(end_time - start_time)

        data = load_json()
        if today_key not in data:
            data[today_key] = {}
        if title in data[today_key]:
            data[today_key][title] += duration
        else:
            data[today_key][title] = duration

        save_json(data)

        # Clear active task when stopped
        if os.path.exists(ACTIVE_TASK_FILE):
            os.remove(ACTIVE_TASK_FILE)

        console.print(f"\n[green]Logged '{title}' for {duration} seconds ({format_time(duration)})[/green]")
        exit(0)

    # Catch Ctrl+C
    signal.signal(signal.SIGINT, handle_exit)

    with Live(console=console, refresh_per_second=1) as live:
        while True:
            elapsed = int(time.time() - start_time)
            live.update(f"Tracking '[bold cyan]{title}[/bold cyan]' - [bold green]{format_time(elapsed)}[/bold green]")
            time.sleep(1)

def format_time(seconds):
    """Format seconds into hr/min/sec string."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}hr {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"

def select_task():
    """Use fzf to select a task interactively with Vim-style navigation and instant selection."""
    data = load_json()
    today_key = datetime.now().strftime("%Y-%m-%d")
    tasks = list(data.get(today_key, {}).keys())

    if not tasks:
        print("No tasks available.")
        return None

    # Run fzf with Vim-style navigation (j/k) and instant selection on Enter
    try:
        task = subprocess.run(
            ["fzf", "--height=10", "--layout=reverse", "--border",
             "--bind", "ctrl-j:down", "--bind", "ctrl-k:up", "--bind", "enter:accept"],
            input="\n".join(tasks), text=True, capture_output=True
        ).stdout.strip()
        return task if task else None
    except FileNotFoundError:
        print("fzf not found. Please install fzf.")
        return None

def get_status():
    """Return current tracking status as JSON."""
    if os.path.exists(ACTIVE_TASK_FILE):
        with open(ACTIVE_TASK_FILE, "r") as f:
            status = json.load(f)
            print(json.dumps(status))
            return

    print(json.dumps({"tracking": False, "current_task": None}))

def main():
    parser = argparse.ArgumentParser(description="Track time spent on tasks.")
    parser.add_argument("title", nargs="?", help="Task title (omit to list tasks)")
    parser.add_argument("--hr", type=int, default=0, help="Start tracking at X hours offset")
    parser.add_argument("--select-task", action="store_true", help="Select a task interactively using fzf")
    parser.add_argument("--status", action="store_true", help="Print tracking status as JSON")

    args = parser.parse_args()

    if args.status:
        get_status()
        return

    if args.select_task:
        task = select_task()
        if task:
            print(task)
        return

    if not args.title:
        list_tasks()
    else:
        track_task(args.title, args.hr * 3600)

if __name__ == "__main__":
    main()
