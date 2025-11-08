"""
CK3 Character Manager - Unified Application
Main entry point for the application.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui import CK3CharacterApp


def main():
    """Main entry point."""
    app = CK3CharacterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
