"""Shared sandbox: the toolkit is copied into a throwaway HOME, so tests never touch the real one.

PD_SRC picks which copy of the toolkit to test (default: the folder above tests/).
say, killall, caffeinate and afinfo are always faked, so tests are silent.
"""
import os
import pathlib
import shutil
import stat
import subprocess
import tempfile
import time

SRC = pathlib.Path(os.environ.get("PD_SRC", pathlib.Path(__file__).resolve().parent.parent / "scripts"))
TOOLS = ["presto", "behold", "go", "speak", "tidy", "pd", "present", "stage.sh",
         "nav.js", "stage.html", "stage2.html", "voice.pl", "gen_report.py"]


def report(title, headlines):
    figs = "".join(
        f'<figure data-say="{h}"><svg viewBox="0 0 1280 720" width="640" height="360">'
        f'<rect width="1280" height="720" fill="#888"/><text x="60" y="80">{h}</text></svg>'
        f"<figcaption>{h}</figcaption></figure>" for h in headlines)
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title></head><body>{figs}</body></html>'


class Sandbox:
    def __init__(self, fake_osascript=True):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="pdt-")).resolve()
        self.home = self.root / "home"
        self.d = self.home / "predigestation"
        self.downloads = self.home / "Downloads"
        self.bin = self.root / "bin"
        for p in (self.d, self.downloads, self.bin):
            p.mkdir(parents=True)
        for name in TOOLS:
            if (SRC / name).exists():
                shutil.copy2(SRC / name, self.d / name)
        (self.d / ".screen").write_text("0\n0\n900\n600\n")
        self.said = self.root / "said.log"
        self.calls = self.root / "osascript.log"
        self._fake("say", f'case " $* " in *" -o "*) exit 1;; esac\necho "$*" >> "{self.said}"')
        self._fake("killall", "exit 0")
        self._fake("caffeinate", "exit 0")
        self._fake("afinfo", "exit 0")
        if fake_osascript:
            self._fake("osascript", f'{{ echo "ARGS $*"; [ -t 0 ] || cat; }} >> "{self.calls}"')

    def _fake(self, name, body):
        p = self.bin / name
        p.write_text(f"#!/bin/bash\n{body}\n")
        p.chmod(p.stat().st_mode | stat.S_IEXEC)

    def run(self, tool, *args, settle=1.2):
        env = dict(os.environ, HOME=str(self.home), PATH=f"{self.bin}:{os.environ['PATH']}")
        r = subprocess.run([str(self.d / tool), *args], env=env, capture_output=True,
                           text=True, timeout=40, stdin=subprocess.DEVNULL)
        time.sleep(settle)  # background tidy and calibration
        return r

    def add_report(self, name, title, headlines, folder=None):
        p = (folder or self.downloads) / name
        p.write_text(report(title, headlines))
        return p

    def read(self, path):
        return path.read_text() if path.exists() else ""

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)
