# text-clipboard
Create custom hotkeys to paste any number of strings / text snippets on your system.

This is an app written in Python 3 using `tkinter` for GUI and the `pynput` module [see docs](https://pynput.readthedocs.io/en/latest/) to detect and execute keypresses. 
* To create hotkeys, I have only implemented Ctrl ⌃/Shift ⇧/Alt ⌥ for modifiers and numeric (0-9) keys so far.
* The app doesn't access the system clipboard or modify it, or register any hotkeys with the system - starting the app activates a `pynput.keyboard.Listener` thread to monitor keyboard input, and when a hotkey combination (as saved from the app) is detected, the main thread triggers keystrokes to type all the corresponding text.
* There are many known issues with `tkinter` on Mac OS - I have only tested this app on Windows 10.
