#!/usr/bin/env python3
"""
Entry point for running the GUI version of the Video Localization Pipeline.
"""

if __name__ == "__main__":
    from gui import LocalizationApp
    app = LocalizationApp()
    app.mainloop()
