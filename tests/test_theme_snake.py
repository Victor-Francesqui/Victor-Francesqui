import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from theme_snake import NEON, theme

SOURCE = (
    '<svg viewBox="-16 -32 880 192" width="880" height="192" xmlns="http://www.w3.org/2000/svg">'
    "<style>:root{--cs:#8B7CFF;--c4:#31D4CE}.s{animation:none linear 12100ms infinite}</style>"
    '<rect class="s" width="12" height="12"/></svg>'
)


class ThemeSnakeTest(unittest.TestCase):
    def test_wraps_animation_in_valid_svg_with_matrix_palette(self):
        result = theme(SOURCE)
        ET.fromstring(result)
        self.assertIn(f"--cs:{NEON}", result)
        self.assertNotIn("#8B7CFF", result)

    def test_slows_the_animation(self):
        self.assertIn("18150ms", theme(SOURCE))

    def test_rain_glyphs_stay_in_a_vertical_column(self):
        root = ET.fromstring(theme(SOURCE))
        rain = [node for node in root.iter("{http://www.w3.org/2000/svg}text") if node.get("class") == "rain"]
        self.assertTrue(rain)
        for node in rain:
            self.assertEqual(len(node.get("x").split()), len(node.text))
            self.assertEqual(set(node.get("x").split()), {"0"})

    def test_rejects_unknown_format(self):
        with self.assertRaises(ValueError):
            theme("<svg></svg>")


if __name__ == "__main__":
    unittest.main()
