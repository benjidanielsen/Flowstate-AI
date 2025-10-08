import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_gods import godmode_brain  # type: ignore  # noqa: E402


class GodmodeBrainTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = TemporaryDirectory()
        tmp_path = Path(self.tmp_dir.name)
        self.plan_path = tmp_path / "plan.json"
        self.status_path = tmp_path / "status.json"
        self.brain = godmode_brain.GodmodeBrain(plan_path=self.plan_path, status_path=self.status_path)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_plan_contains_three_phases(self) -> None:
        phases = self.brain.plan["phases"]
        self.assertEqual(3, len(phases))
        self.assertEqual(
            ["phase_1_ai_brain", "phase_2_crm_delivery", "phase_3_launch"],
            [phase["key"] for phase in phases],
        )

    def test_update_status_records_current_phase(self) -> None:
        status = self.brain.update_status(
            current_phase="phase_2_crm_delivery", completed_phases=["phase_1_ai_brain"], notes="testing"
        )
        self.assertEqual("phase_2_crm_delivery", status["current_phase"])
        with self.status_path.open("r", encoding="utf-8") as handle:
            disk_status = json.load(handle)
        self.assertEqual(status["current_phase"], disk_status["current_phase"])
        self.assertIn("next_milestone", status)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

