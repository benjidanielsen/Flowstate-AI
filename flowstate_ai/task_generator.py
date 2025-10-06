import datetime

class TaskGenerator:
    def __init__(self, project_name="Flowstate-AI"):
        self.project_name = project_name

    def generate_next_week_tasks(self):
        """
        Generates a comprehensive list of tasks for the upcoming week (week 2).
        Returns a list of task dictionaries with details.
        """
        # Determine next week's date range
        today = datetime.date.today()
        # Calculate next Monday
        next_monday = today + datetime.timedelta(days=(7 - today.weekday()))
        next_sunday = next_monday + datetime.timedelta(days=6)

        tasks = [
            {
                "title": "Design AI Task Generation Algorithm",
                "description": "Create algorithm specs for generating weekly tasks automatically.",
                "due_date": next_monday.isoformat(),
                "priority": "High",
                "assigned_to": "AI Module"
            },
            {
                "title": "Implement Task Generation Module",
                "description": "Develop Python module that produces next week's comprehensive task list.",
                "due_date": (next_monday + datetime.timedelta(days=2)).isoformat(),
                "priority": "High",
                "assigned_to": "Backend Team"
            },
            {
                "title": "Integrate Task Generator with Project Dashboard",
                "description": "Connect task generation module output with the project management dashboard UI.",
                "due_date": (next_monday + datetime.timedelta(days=4)).isoformat(),
                "priority": "Medium",
                "assigned_to": "Frontend Team"
            },
            {
                "title": "Write Unit Tests for Task Generator",
                "description": "Ensure coverage and correctness of the task generation module.",
                "due_date": (next_monday + datetime.timedelta(days=5)).isoformat(),
                "priority": "Medium",
                "assigned_to": "QA Team"
            },
            {
                "title": "Review and Refine Generated Tasks",
                "description": "Conduct review meeting to refine and approve generated tasks for week 2.",
                "due_date": next_sunday.isoformat(),
                "priority": "Low",
                "assigned_to": "Project Managers"
            }
        ]

        return {
            "project": self.project_name,
            "week_start": next_monday.isoformat(),
            "week_end": next_sunday.isoformat(),
            "tasks": tasks
        }

if __name__ == "__main__":
    generator = TaskGenerator()
    next_week_tasks = generator.generate_next_week_tasks()
    import json
    print(json.dumps(next_week_tasks, indent=4))
