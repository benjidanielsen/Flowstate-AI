#!/usr/bin/env python3
"""
GODMODE Brain Orchestrator
Manages the three-phase, nine-hour launch sequence for Flowstate-AI
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class GodmodeBrain:
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).parent.parent
        self.memory_dir = self.root_dir / "collective-memory"
        self.plan_file = self.memory_dir / "godmode_brain_plan.json"
        self.status_file = self.memory_dir / "project_status.json"
        self.work_log_file = self.root_dir / "AUTONOMOUS_WORK_LOG.md"
        
    def load_plan(self) -> Dict:
        """Load the GODMODE Brain plan from JSON"""
        if not self.plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {self.plan_file}")
        with open(self.plan_file, 'r') as f:
            return json.load(f)
    
    def load_status(self) -> Dict:
        """Load the current project status"""
        if not self.status_file.exists():
            # Initialize with default status
            return {
                "current_phase": "phase_1_ai_brain",
                "completed_phases": [],
                "phase_order": ["phase_1_ai_brain", "phase_2_crm_delivery", "phase_3_launch"],
                "system_status": "IN_PROGRESS",
                "updated_at": datetime.now().isoformat(),
                "next_milestone": (datetime.now() + timedelta(hours=3)).isoformat()
            }
        with open(self.status_file, 'r') as f:
            return json.load(f)
    
    def save_status(self, status: Dict):
        """Save the project status"""
        status["last_updated"] = datetime.now().isoformat()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def set_phase(self, phase_number: int):
        """Set the current phase"""
        plan = self.load_plan()
        phases = plan.get("phases", [])
        
        if phase_number < 1 or phase_number > len(phases):
            raise ValueError(f"Invalid phase number: {phase_number}. Must be between 1 and {len(phases)}")
        
        phase = phases[phase_number - 1]
        status = self.load_status()
        status["current_phase"] = phase_number
        status["phase_name"] = phase["name"]
        status["phase_start_time"] = datetime.now().isoformat()
        status["next_milestone"] = (datetime.now() + timedelta(hours=3)).isoformat()
        status["completion_percentage"] = ((phase_number - 1) / len(phases)) * 100
        
        self.save_status(status)
        print(f"✅ Phase {phase_number} set: {phase['name']}")
        print(f"📅 Next milestone: {status['next_milestone']}")
    
    def get_status(self):
        """Display current status"""
        status = self.load_status()
        plan = self.load_plan()
        
        current_phase_key = status.get('current_phase', 'phase_1_ai_brain')
        completed = status.get('completed_phases', [])
        phase_order = status.get('phase_order', [])
        
        # Find current phase in plan
        current_phase_data = None
        for phase in plan.get("phases", []):
            if phase.get("key") == current_phase_key:
                current_phase_data = phase
                break
        
        print("\n" + "="*60)
        print("🧠 GODMODE BRAIN STATUS")
        print("="*60)
        print(f"Current Phase: {current_phase_key}")
        if current_phase_data:
            print(f"Title: {current_phase_data.get('title', 'Unknown')}")
        print(f"System Status: {status.get('system_status', 'UNKNOWN')}")
        print(f"Next Milestone: {status.get('next_milestone', 'Not set')}")
        print(f"Completed Phases: {len(completed)}/{len(phase_order)}")
        print(f"Last Updated: {status.get('updated_at', 'Unknown')}")
        print("="*60 + "\n")
        
        # Show current phase details
        if current_phase_data:
            print(f"📋 Current Phase Tasks:")
            for i, task in enumerate(current_phase_data.get("tasks", []), 1):
                print(f"  {i}. {task}")
            print()
    
    def list_phases(self):
        """List all phases"""
        plan = self.load_plan()
        status = self.load_status()
        
        print("\n" + "="*60)
        print("🧠 GODMODE BRAIN PHASES")
        print("="*60)
        
        for i, phase in enumerate(plan.get("phases", []), 1):
            marker = "👉" if i == status["current_phase"] else "  "
            print(f"{marker} Phase {i}: {phase['name']}")
            print(f"   Duration: {phase['duration']}")
            print(f"   Objective: {phase['objective']}")
            print()
    
    def complete_phase(self, phase_number: int, notes: str = ""):
        """Mark a phase as complete and advance to next"""
        plan = self.load_plan()
        phases = plan.get("phases", [])
        
        if phase_number < 1 or phase_number > len(phases):
            raise ValueError(f"Invalid phase number: {phase_number}")
        
        status = self.load_status()
        
        # Log completion
        completion_log = {
            "phase": phase_number,
            "phase_name": phases[phase_number - 1]["name"],
            "completed_at": datetime.now().isoformat(),
            "notes": notes
        }
        
        # Advance to next phase if available
        if phase_number < len(phases):
            self.set_phase(phase_number + 1)
            print(f"✅ Phase {phase_number} completed!")
            print(f"🚀 Advanced to Phase {phase_number + 1}")
        else:
            status["completion_percentage"] = 100
            self.save_status(status)
            print(f"🎉 All phases complete! GODMODE Brain launch successful!")
    
    def generate_work_log(self):
        """Generate the AUTONOMOUS_WORK_LOG.md file"""
        plan = self.load_plan()
        status = self.load_status()
        
        current_phase_key = status.get('current_phase', 'phase_1_ai_brain')
        completed = status.get('completed_phases', [])
        phase_order = status.get('phase_order', [])
        progress = (len(completed) / len(phase_order)) * 100 if phase_order else 0
        
        content = f"""# AUTONOMOUS WORK LOG

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Status

- **Phase:** {current_phase_key}
- **Progress:** {progress:.1f}%
- **Next Milestone:** {status.get('next_milestone', 'Not set')}

## Command Board Rules

1. **Claim Before Work:** No task begins until an owner signs the work log
2. **Log Outcomes:** Every deliverable includes references to commits, logs, or artifacts
3. **Keep the Brain Updated:** Use `python ai-gods/godmode_brain.py --set-phase <phase>` to advance
4. **Preserve Institutional Memory:** Summaries go into `collective-memory/`

## Phase Tasks

"""
        
        for i, phase in enumerate(plan.get("phases", []), 1):
            phase_key = phase.get("key", "")
            is_current = phase_key == current_phase_key
            is_completed = phase_key in completed
            marker = "🔥" if is_current else "✅" if is_completed else "⏳"
            content += f"\n### {marker} Phase {i}: {phase.get('title', 'Unknown')}\n\n"
            content += f"**Duration:** {phase.get('timebox_hours', 3)} hours  \n"
            content += f"**Objective:** {phase.get('objective', 'N/A')}\n\n"
            content += "| Task | Owner | Status | Notes |\n"
            content += "|------|-------|--------|-------|\n"
            
            for task in phase.get("tasks", []):
                content += f"| {task} | | ⏳ | |\n"
            content += "\n"
        
        content += """
## Status Commands

```bash
# View current status
python ai-gods/godmode_brain.py --status

# List all phases
python ai-gods/godmode_brain.py --list-phases

# Set current phase
python ai-gods/godmode_brain.py --set-phase <number>

# Complete phase and advance
python ai-gods/godmode_brain.py --complete-phase <number> --notes "completion notes"
```
"""
        
        with open(self.work_log_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Work log generated: {self.work_log_file}")

def main():
    parser = argparse.ArgumentParser(description="GODMODE Brain Orchestrator")
    parser.add_argument("--status", action="store_true", help="Display current status")
    parser.add_argument("--list-phases", action="store_true", help="List all phases")
    parser.add_argument("--set-phase", type=int, help="Set current phase number")
    parser.add_argument("--complete-phase", type=int, help="Complete phase and advance")
    parser.add_argument("--notes", type=str, default="", help="Completion notes")
    parser.add_argument("--generate-log", action="store_true", help="Generate work log")
    
    args = parser.parse_args()
    brain = GodmodeBrain()
    
    try:
        if args.status:
            brain.get_status()
        elif args.list_phases:
            brain.list_phases()
        elif args.set_phase:
            brain.set_phase(args.set_phase)
        elif args.complete_phase:
            brain.complete_phase(args.complete_phase, args.notes)
        elif args.generate_log:
            brain.generate_work_log()
        else:
            brain.get_status()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

