import unittest
from datetime import date, timedelta
from src.kensho.models import ClockUnit, SECONDS_PER_MINUTE

class TestClockUnit(unittest.TestCase):
    def setUp(self):
        self.clock = ClockUnit(
            identifier="C1",
            label="Test Clock",
            interval_minutes=10
        )

    def test_initialization(self):
        self.assertEqual(self.clock.identifier, "C1")
        self.assertEqual(self.clock.label, "Test Clock")
        self.assertEqual(self.clock.interval_minutes, 10)
        self.assertEqual(self.clock.elapsed_seconds, 0.0)
        self.assertFalse(self.clock.paused)
        self.assertFalse(self.clock.due)

    def test_tick_advances_time(self):
        completed = self.clock.tick(1.0)
        self.assertFalse(completed)
        self.assertEqual(self.clock.elapsed_seconds, 1.0)

    def test_tick_completes_interval(self):
        # Advance to just before completion
        total_seconds = 10 * SECONDS_PER_MINUTE
        self.clock.elapsed_seconds = total_seconds - 0.5
        
        completed = self.clock.tick(1.0)
        self.assertTrue(completed)
        self.assertTrue(self.clock.due)
        self.assertEqual(self.clock.elapsed_seconds, total_seconds)

    def test_reset(self):
        self.clock.elapsed_seconds = 50.0
        self.clock.due = True
        self.clock.paused = True
        
        self.clock.reset()
        
        self.assertEqual(self.clock.elapsed_seconds, 0.0)
        self.assertFalse(self.clock.due)
        self.assertFalse(self.clock.paused)
        self.assertEqual(self.clock.check_ins_today, 1)

    def test_ensure_today_rollover(self):
        # Simulate yesterday
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        self.clock.last_check_in_date = yesterday
        self.clock.check_ins_today = 5
        self.clock.history[yesterday] = 5
        
        self.clock.ensure_today()
        
        self.assertEqual(self.clock.last_check_in_date, date.today().isoformat())
        self.assertEqual(self.clock.check_ins_today, 0)
        self.assertEqual(self.clock.history[yesterday], 5)

    def test_serialization(self):
        self.clock.elapsed_seconds = 120.0
        data = self.clock.serialize()
        
        new_clock = ClockUnit.from_dict(data)
        self.assertEqual(new_clock.identifier, self.clock.identifier)
        self.assertEqual(new_clock.elapsed_seconds, 120.0)

if __name__ == '__main__':
    unittest.main()
