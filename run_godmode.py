import sys
import os
import runpy

# Add the project root to the Python path to resolve module imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # Run the godmode_brain module as the main entry point
    # This is equivalent to running `python -m ai_gods.godmode_brain`
    # from the root directory.
    runpy.run_module("ai_gods.godmode_brain", run_name="__main__")
