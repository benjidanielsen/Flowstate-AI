import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_gods.godmode_brain import GodmodeBrain


def main():
    """
    Initializes the GodmodeBrain and triggers the project analysis.
    """
    print("🚀 Initializing GODMODE Brain...")
    try:
        brain = GodmodeBrain()
        print("🧠 GODMODE Brain Initialized. Analyzing project and creating plan...")

        # This is a placeholder for the actual analysis and plan creation method
        # In the real implementation, this would be a more complex call.
        # For now, we'll just generate the plan and update the status.
        brain._generate_plan()
        brain.update_status(
            notes="Initial analysis complete. System is ready for autonomous operation."
        )

        print("✅ Project analysis complete. New plan generated and status updated.")
        print(f"📄 Plan file located at: {brain.plan_path.resolve()}")
        print(f"📊 Status file located at: {brain.status_path.resolve()}")

    except Exception as e:
        print(f"❌ An error occurred during brain initialization or analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
