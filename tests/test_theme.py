"""Day or night comes from the laptop's clock alone: no location is stored anywhere."""
import re
import subprocess
import unittest

from harness import SRC

PAGES = ["stage.html", "stage2.html", "present"]


class Theme(unittest.TestCase):
    def test_no_location_in_the_code(self):
        for name in PAGES:
            self.assertIsNone(re.search(r"\b(LAT|LON|latitude|longitude)\b", (SRC / name).read_text()), name)

    def is_day(self, name, hour, minute):
        text = (SRC / name).read_text()
        fn = re.search(r"function isDay\(d\)\{[^}]*\}", text)
        self.assertIsNotNone(fn, f"{name} has no isDay()")
        r = subprocess.run(["node", "-e", f"{fn.group(0)};console.log(isDay(new Date(2026,10,26,{hour},{minute})))"],
                           capture_output=True, text=True)
        return r.stdout.strip() == "true"

    def test_light_from_seven_to_seven(self):
        for name in PAGES:
            got = [self.is_day(name, h, m) for h, m in ((6, 59), (7, 0), (18, 59), (19, 0), (0, 0))]
            self.assertEqual(got, [False, True, True, False, False], name)


if __name__ == "__main__":
    unittest.main()
