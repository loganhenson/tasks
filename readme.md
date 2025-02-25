# Track - CLI Time Tracker with FZF

Track is a simple command-line tool to track time spent on tasks with an **interactive FZF-based selection menu**.

## Features
- 🕒 **Track time on tasks** effortlessly.
- 🔍 **Interactive fuzzy search** using [FZF](https://github.com/junegunn/fzf).
- 🎛 **Vim-style navigation** (`Ctrl-J` / `Ctrl-K` to move up/down).
- ⚡ **Auto-runs immediately** after task selection.
- 📜 **Displays tracked tasks in a structured format**.

## Installation

### 1️⃣ Install Dependencies

#### **Mac (Homebrew)**
```sh
brew install fzf
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.in
```

#### **Ubuntu/Debian**
```sh
sudo apt install fzf python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.in
```

### 2️⃣ Add Auto-Completion to `.zshrc`
To enable **TAB-based task selection**, add this to your `~/.zshrc`:

```sh
autoload -Uz compinit && compinit

_track_autocomplete() {
    # Only trigger if we're completing a 'track' command
    [[ $LBUFFER == track* ]] || { zle expand-or-complete; return }

    # Capture the selected task from fzf
    local task
    task=$(/Users/loganhenson/Desktop/track/.venv/bin/python /Users/loganhenson/Desktop/track/track.py --select-task)

    # Insert the selected task into the command line and auto-run it
    if [[ -n $task ]]; then
        LBUFFER+=" \"$task\""
        zle accept-line  # Auto-run the command immediately
    fi
}

zle -N _track_autocomplete
bindkey '^I' _track_autocomplete  # Override TAB, but only when starting with 'track'
compdef _track_autocomplete track
```

Reload your shell:
```sh
source ~/.zshrc
```

## Usage

### **📜 List Tracked Tasks**
```sh
track
```
_Shows a table of all tracked tasks._

### **🕒 Start Tracking a Task**
```sh
track "New Feature Development"
```
_Starts tracking the specified task._

### **🔥 Select a Task Using FZF**
```sh
track <TAB>
```
_Opens an interactive menu to select a task._

### **🎬 Stop Tracking**
Press `Ctrl + C` while tracking to stop and log the task duration.

## How It Works
- Stores tracked time in `~/track.json`
- Uses `FZF` for quick task selection
- Enables `<TAB>` completion for task selection
- Logs tasks in a structured format for easy retrieval

Now you can easily track your tasks with a simple CLI command! 🚀

### BONUS
OSX Menu Bar Icon

```shell
python menu_bar_tracker.py &
```

