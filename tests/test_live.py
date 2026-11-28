"""Real Safari, silent. Opens throwaway windows that stand in for your own tabs, then closes them.

Run: PD_LIVE=1 python3 -m unittest discover -s tests -p 'test_live.py' -v
It takes over the screen for about a minute.
"""
import os
import subprocess
import time
import unittest

from harness import Sandbox


def osa(script, *args):
    r = subprocess.run(["/usr/bin/osascript", "-", *args], input=script, capture_output=True,
                       text=True, timeout=30)
    if r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.rstrip("\n")


def window_ids():
    out = osa('tell application "Safari"\nset o to ""\nrepeat with w in windows\n'
              'if visible of w then set o to o & (id of w) & linefeed\nend repeat\nreturn o\nend tell')
    return {int(x) for x in out.split()}


def new_window(url):
    return int(osa('on run argv\ntell application "Safari"\nmake new document with properties '
                   '{URL:item 1 of argv}\nset i to id of front window\nend tell\ndelay 0.6\nreturn i\nend run', url))


def urls(wid):
    out = osa('on run argv\ntell application "Safari"\nset o to ""\n'
              'repeat with t in tabs of window id ((item 1 of argv) as integer)\n'
              'set o to o & (URL of t) & linefeed\nend repeat\nreturn o\nend tell\nend run', str(wid))
    return out.split("\n") if out else []


def front(wid):
    osa('on run argv\ntell application "Safari" to set index of window id ((item 1 of argv) as integer) to 1\n'
        'delay 0.3\nend run', str(wid))


def add_tab(wid, url):
    osa('on run argv\ntell application "Safari" to tell window id ((item 1 of argv) as integer) to '
        'make new tab with properties {URL:item 2 of argv}\ndelay 0.6\nend run', str(wid), url)


def close(wid):
    try:
        osa('on run argv\ntell application "Safari" to close window id ((item 1 of argv) as integer)\nend run', str(wid))
    except RuntimeError:
        pass


@unittest.skipUnless(os.environ.get("PD_LIVE") == "1", "set PD_LIVE=1 to drive real Safari")
class Live(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox(fake_osascript=False)
        self.before = window_ids()
        self.addCleanup(self.cleanup)
        self.box.add_report("coffee-report.html", "Coffee report",
                            ["Weekend sales nearly doubled", "Lattes were the favourite drink",
                             "8 am is the morning rush"])
        # A "personal" local report: the kind of tab the old code closed.
        self.mine = self.box.add_report("my-own-report.html", "Mine", ["Private"], folder=self.box.root)

    def cleanup(self):
        # Close only windows that did not exist before this test.
        for wid in window_ids() - self.before:
            close(wid)
        self.box.close()

    def decoy(self):
        wid = new_window(f"file://{self.mine}")
        return wid, urls(wid)

    def stage(self):
        r = self.box.run("presto")
        self.assertEqual(r.stdout.strip(), "on", r.stdout + r.stderr)
        return int((self.box.d / ".stage_window").read_text())

    def test_commands_leave_your_front_tab_alone_when_stage_off(self):
        wid, was = self.decoy()
        for cmd in (("speak", "Hi"), ("go", "next"), ("pd", "Hi"), ("tidy",)):
            self.box.run(*cmd)
            self.assertEqual(urls(wid), was, cmd)

    def test_commands_use_stage_even_when_your_window_is_in_front(self):
        stage = self.stage()
        wid, was = self.decoy()
        for cmd in (("speak", "Hi"), ("behold", "coffee report"), ("go", "next"), ("pd", "Hi")):
            front(wid)
            self.box.run(*cmd)
            self.assertEqual(urls(wid), was, cmd)
        self.assertIn("stage2.html", urls(stage)[0])

    def test_behold_and_go_really_move_on_the_stage(self):
        stage = self.stage()
        r = self.box.run("behold", "coffee report")
        self.assertIn("chart 1 of 3", r.stdout, r.stdout + r.stderr)
        self.assertIn("coffee-report.html", urls(stage)[0])
        r = self.box.run("go", "next")
        self.assertIn("slide 2: Lattes", r.stdout, r.stdout + r.stderr)
        self.box.run("speak", "A detour")
        r = self.box.run("go", "next")
        self.assertIn("slide 3: 8 am", r.stdout, r.stdout + r.stderr)

    def test_closed_stage_means_voice_only_except_behold(self):
        stage = self.stage()
        close(stage)
        wid, was = self.decoy()
        count = len(window_ids())
        for cmd in (("speak", "Hi"), ("go", "next"), ("pd", "Hi")):
            self.box.run(*cmd)
            self.assertEqual(urls(wid), was, cmd)
            self.assertEqual(len(window_ids()), count, cmd)
        r = self.box.run("behold", "coffee report")
        self.assertIn("chart 1 of 3", r.stdout, r.stdout + r.stderr)
        self.assertEqual(urls(wid), was)
        self.assertEqual(len(window_ids()), count + 1)

    def test_stage_window_browsed_elsewhere_is_left_alone(self):
        stage = self.stage()
        osa('on run argv\ntell application "Safari" to set URL of current tab of window id '
            '((item 1 of argv) as integer) to item 2 of argv\ndelay 0.6\nend run', str(stage), f"file://{self.mine}")
        was = urls(stage)
        self.box.run("speak", "Hi")
        self.assertEqual(urls(stage), was)

    def test_off_closes_the_stage_but_not_your_report_tabs(self):
        wid, was = self.decoy()
        stage = self.stage()
        self.box.run("behold", "coffee report")
        r = self.box.run("presto")
        self.assertTrue(r.stdout.startswith("off"), r.stdout + r.stderr)
        self.assertEqual(urls(wid), was)
        self.assertNotIn(stage, window_ids())
        self.assertFalse((self.box.d / ".stage_window").exists())

    def test_off_keeps_a_tab_you_added_to_the_stage_window(self):
        stage = self.stage()
        add_tab(stage, f"file://{self.mine}")
        osa('on run argv\ntell application "Safari" to tell window id ((item 1 of argv) as integer) to '
            'set current tab to tab 1\nend run', str(stage))
        self.box.run("tidy")
        self.assertEqual(len(urls(stage)), 2)
        self.box.run("presto")
        self.assertEqual([u.split("/")[-1] for u in urls(stage)], ["my-own-report.html"])

    def test_report_name_with_spaces_keeps_its_place(self):
        self.box.add_report("q3 tea sales.html", "Tea", ["Tea one", "Tea two", "Tea three"])
        stage = self.stage()
        r = self.box.run("behold", "tea sales")
        self.assertIn("chart 1 of 3", r.stdout, r.stdout + r.stderr)
        first = urls(stage)[0]
        r = self.box.run("go", "next")
        self.assertIn("slide 2: Tea two", r.stdout, r.stdout + r.stderr)
        self.assertEqual(urls(stage)[0], first, "go reloaded the page")


if __name__ == "__main__":
    unittest.main()
