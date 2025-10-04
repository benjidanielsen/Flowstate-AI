import os
import runpy
import sys

# Add the project root to the Python path to resolve module imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # This allows the script to pass command-line arguments to the module it runs.
    sys.argv = sys.argv
    # Run the godmode_brain module as the main entry point
    # This is equivalent to running `python -m ai_gods.godmode_brain`
    # from the root directory.
    runpy.run_module("ai_gods.godmode_brain", run_name="__main__")
