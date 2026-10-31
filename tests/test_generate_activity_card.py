import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from generate_activity_card import render_card, summarize


def user_with(counts, total=None):
    days = [{"contributionCount": count} for count in counts]
    return {
        "repositories": {"totalCount": 12},
        "contributionsCollection": {
            "contributionCalendar": {
                "totalContributions": sum(counts) if total is None else total,
                "weeks": [{"contributionDays": days}],
            }
        },
    }


class ActivityCardTest(unittest.TestCase):
    def test_counts_active_days_and_longest_streak(self):
        values = [value for value, _ in summarize(user_with([1, 2, 0, 3, 1, 1, 0]))]
        self.assertEqual(values, [8, 5, 3, 12])

    def test_handles_calendar_without_contributions(self):
        values = [value for value, _ in summarize(user_with([0, 0]))]
        self.assertEqual(values, [0, 0, 0, 12])

    def test_renders_valid_svg_with_every_value_for_each_theme(self):
        stats = summarize(user_with([1, 0, 4]))
        for theme in ("dark", "light"):
            svg = render_card(stats, theme)
            ET.fromstring(svg)
            for value, label in stats:
                self.assertIn(f">{value}</text>", svg)
                self.assertIn(label, svg)


if __name__ == "__main__":
    unittest.main()
