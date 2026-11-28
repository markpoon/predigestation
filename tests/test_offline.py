"""No Safari, no sound. Run: python3 -m unittest discover -s tests -p 'test_offline.py' -v"""
import json
import subprocess
import time
import unittest

from harness import SRC, Sandbox


class Base(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox()
        self.addCleanup(self.box.close)
        self.box.add_report("coffee-report.html", "Coffee report",
                            ["Weekend sales nearly doubled", "Lattes were the favourite drink",
                             "8 am is the morning rush"])

    def assertSafariUntouched(self):
        self.assertNotIn("Safari", self.box.read(self.box.calls))


class StageOff(Base):
    """Plan, Next 3: with the stage off, voice only."""

    def test_speak_only_speaks(self):
        self.box.run("speak", "Hello there")
        self.assertIn("Hello there", self.box.read(self.box.said))
        self.assertSafariUntouched()

    def test_pd_only_speaks(self):
        self.box.run("pd", "Big number", "c=big&s=Sales~5")
        self.assertIn("Big number", self.box.read(self.box.said))
        self.assertSafariUntouched()

    def test_behold_speaks_first_headline_if_no_stage_can_open(self):
        r = self.box.run("behold", "coffee report")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Weekend sales nearly doubled", self.box.read(self.box.said))

    def test_go_moves_by_number_and_step(self):
        report = self.box.downloads / "coffee-report.html"
        (self.box.d / ".last").write_text(f"{report}|0\n")
        self.box.run("go", "next")
        self.box.run("go", "3")
        self.box.run("go", "back")
        said = self.box.read(self.box.said).splitlines()
        self.assertEqual([s.split("185 ")[1] for s in said],
                         ["Lattes were the favourite drink",
                          "8 am is the morning rush", "Lattes were the favourite drink"])
        self.assertSafariUntouched()

    def test_tidy_does_nothing_to_safari(self):
        self.box.run("tidy")
        self.assertSafariUntouched()


class StartingTheStage(Base):
    """behold and present turn the stage on themselves; abra is presto with a spoken reply."""

    def setUp(self):
        super().setUp()
        self.box.fake_stage()
        self.report = str(self.box.downloads / "coffee-report.html")

    def said(self):
        return self.box.read(self.box.said)

    def test_behold_turns_the_stage_on(self):
        self.box.run("behold", "coffee report")
        self.assertEqual(self.box.stages_opened(), 1)
        self.assertTrue((self.box.d / ".presto_on").exists())
        self.assertNotIn("cadabra", self.said())

    def test_present_turns_the_stage_on(self):
        r = self.box.run("present", self.report, "0")
        self.assertEqual(self.box.stages_opened(), 1, r.stdout + r.stderr)
        self.assertIn('"slides":3', r.stdout)

    def test_open_stage_is_reused(self):
        self.box.run("presto")
        self.box.run("behold", "coffee report")
        self.box.run("present", self.report, "0")
        self.assertEqual(self.box.stages_opened(), 1)

    def test_closed_stage_is_reopened_not_toggled_off(self):
        self.box.run("presto")
        (self.box.root / "stage.up").unlink()
        self.box.run("behold", "coffee report")
        self.assertEqual(self.box.stages_opened(), 2)
        self.assertTrue((self.box.d / ".presto_on").exists())

    def test_refused_request_opens_nothing(self):
        self.box.run("behold", "zebra budget")
        self.box.run("present", "/nowhere/zebra.html")
        empty = self.box.add_report("empty.html", "Empty", [])
        self.box.run("present", str(empty))
        self.assertEqual(self.box.stages_opened(), 0)

    def test_abra_turns_the_stage_on_and_says_cadabra(self):
        r = self.box.run("abra")
        self.assertEqual(r.stdout.strip(), "on", r.stdout + r.stderr)
        self.assertEqual(self.box.stages_opened(), 1)
        self.assertIn("cadabra", self.said())

    def test_abra_again_turns_the_stage_off(self):
        self.box.run("abra")
        r = self.box.run("abra")
        self.assertTrue(r.stdout.startswith("off"), r.stdout + r.stderr)
        self.assertEqual(self.said().count("cadabra"), 1)
        self.assertFalse((self.box.d / ".presto_on").exists())

    def test_presto_does_not_say_cadabra(self):
        self.box.run("presto")
        self.assertNotIn("cadabra", self.said())


class Replying(Base):
    """reply: Claude's spoken answers, which must not cover a presentation or a chart."""

    def setUp(self):
        super().setUp()
        self.box.fake_stage()
        self.box.run("presto")

    def showing(self, page):
        (self.box.root / "tab.url").write_text(f"file://{self.box.d}/{page}\n")

    def presenting(self):
        sleeper = subprocess.Popen(["sleep", "30"])
        self.addCleanup(sleeper.wait)
        self.addCleanup(sleeper.kill)  # cleanups run last-first
        (self.box.d / ".presenting").write_text(f"{sleeper.pid}\n")

    def said(self):
        return self.box.read(self.box.said)

    def page_changes(self):
        return sum(l.startswith("ARGS") and "stage.html#t=" in l for l in self.box.read(self.box.calls).splitlines())

    def test_word_page_gets_words_and_voice(self):
        self.showing("stage.html")
        self.box.run("reply", "Hello there")
        self.assertIn("Hello there", self.said())
        self.assertEqual(self.page_changes(), 1)

    def test_chart_stays_up_while_replying(self):
        self.showing("report.html?pdk=1")
        self.box.run("reply", "Hello there")
        self.assertIn("Hello there", self.said())
        self.assertEqual(self.page_changes(), 0)
        self.assertFalse((self.box.d / ".interjecting").exists())

    def test_speaks_during_a_presentation_by_default(self):
        self.showing("presenter.html#1")
        self.presenting()
        self.box.run("reply", "Hello there")
        self.assertIn("Hello there", self.said())
        self.assertEqual(self.page_changes(), 0)

    def test_toggle_off_keeps_quiet_during_a_presentation_only(self):
        self.assertIn("off", self.box.run("interject").stdout)
        self.showing("presenter.html#1")
        self.presenting()
        self.box.run("reply", "Not now")
        self.assertNotIn("Not now", self.said())
        (self.box.d / ".presenting").unlink()
        self.showing("stage.html")
        self.box.run("reply", "Now is fine")
        self.assertIn("Now is fine", self.said())

    def focused(self):
        return self.box.read(self.box.calls).count("reply: focus stage")

    def test_stage_is_brought_forward_before_speaking(self):
        for page in ("stage.html", "report.html?pdk=1"):
            self.box.calls.write_text("")
            self.showing(page)
            self.box.run("reply", "Hello there")
            self.assertGreater(self.focused(), 0, page)

    def test_focus_is_not_taken_when_quiet_or_stage_off(self):
        self.box.run("interject", "off")
        self.showing("presenter.html#1")
        self.presenting()
        self.box.run("reply", "Not now")
        (self.box.d / ".presenting").unlink()
        (self.box.root / "stage.up").unlink()
        self.box.run("reply", "No stage")
        self.assertEqual(self.focused(), 0)

    def test_toggle_goes_back_on_and_takes_a_word(self):
        self.assertIn("off", self.box.run("interject", "off").stdout)
        self.assertIn("off", self.box.run("interject", "off").stdout)
        self.assertIn("on", self.box.run("interject").stdout)
        self.assertIn("on", self.box.run("interject", "on").stdout)

    def test_presentation_waits_while_a_reply_is_spoken(self):
        lock = self.box.d / ".interjecting"
        lock.write_text("")
        self.box.run("present", str(self.box.downloads / "coffee-report.html"), "0", settle=0.8)
        self.assertNotIn("Weekend", self.said())
        self.assertTrue((self.box.d / ".presenting").exists())
        lock.unlink()
        time.sleep(4)
        self.assertIn("8 am is the morning rush", self.said())
        self.assertFalse((self.box.d / ".presenting").exists())


class FindingDocuments(Base):
    def found(self, query):
        return self.box.run("behold", query, settle=0.2)

    def assertRefused(self, query):
        r = self.found(query)
        self.assertNotEqual(r.returncode, 0, f"{query!r} opened something: {r.stdout}")
        self.assertIn("no document found", r.stdout)
        self.assertNotIn("Weekend", self.box.read(self.box.said))

    def test_unknown_document_is_refused(self):
        self.assertRefused("the zebra budget")

    def test_half_a_match_is_refused(self):
        self.assertRefused("coffee budget")

    def test_only_filler_words_is_refused(self):
        self.assertRefused("the report")

    def test_empty_request_is_refused(self):
        self.assertRefused("")

    def test_missing_path_is_refused(self):
        self.assertRefused("/nowhere/zebra.html")

    def test_name_with_filler_words_is_found(self):
        r = self.found("behold the coffee report")
        self.assertIn("coffee-report.html", r.stdout)

    def test_title_matches_when_file_name_does_not(self):
        self.box.add_report("x1.html", "Quarterly staffing", ["Staff grew"])
        r = self.found("staffing")
        self.assertIn("x1.html", r.stdout)

    def test_exact_path_is_used(self):
        p = self.box.add_report("odd name.html", "Odd", ["Odd one"])
        r = self.found(str(p))
        self.assertIn("odd name.html", r.stdout)


class Pieces(unittest.TestCase):
    def node(self, script):
        r = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_voice_estimate_grows_with_text_and_pauses(self):
        box = Sandbox()
        self.addCleanup(box.close)

        def est(text):
            r = subprocess.run(["perl", str(box.d / "voice.pl"), "est", text], capture_output=True,
                               text=True, env={"HOME": str(box.home)})
            return float(r.stdout)

        self.assertLess(est("hi"), est("hi there everyone"))
        self.assertLess(est("one two"), est("one. two"))

    def test_chart_navigation_clamps_and_finds(self):
        nav = (SRC / "nav.js").read_text()
        out = self.node("""
          const fig=(say,svg)=>({textContent:say,getAttribute(k){return k==='data-say'?say:this['_'+k]},
            setAttribute(k,v){this['_'+k]=v},querySelector:()=>({innerHTML:svg,querySelector:()=>null,
            getBoundingClientRect:()=>({left:0,top:0,width:600,height:300})})});
          const figs=[fig('Weekend sales',''),fig('Lattes favourite',' A5 L1,1 A2'),fig('Morning rush','')];
          global.window=global; global.innerWidth=1200; global.innerHeight=800;
          global.document={querySelectorAll:()=>figs,documentElement:{style:{}},body:{style:{}}};
          global.scrollTo=()=>{};
          eval(%s);
          console.log(JSON.stringify([pdto(99),pdrel(-99),pdrel(1),pdfind('the latte one'),
            pdfind('donut'),pdfind('zebra'),cur]));
        """ % json.dumps(nav))
        self.assertEqual(out, [2, 0, 1, 1, 1, -1, 1])

    def test_stage_words_run_slightly_ahead_of_the_voice(self):
        script = (SRC / "stage.html").read_text().split("<script>")[-1].split("</script>")[0]
        out = self.node("""
          let now=0, frame=null; const box={style:{},textContent:''};
          Date.now=()=>now; global.requestAnimationFrame=f=>{frame=f};
          global.window=global; global.addEventListener=()=>{};
          global.document={getElementById:()=>box};
          global.location={hash:'#t=0&d=2&w=one,%%20two.'};
          eval(%s);
          const seen={};
          for(now=-500;now<2000&&frame;now+=10){const f=frame;frame=null;f();
            if(box.textContent&&!(box.textContent in seen))seen[box.textContent]=now;}
          console.log(JSON.stringify(seen));
        """ % json.dumps(script))
        # The voice model puts "one" at 0.12 s; the screen leads it by 0.15 s.
        self.assertEqual(out, {"ONE": -30, "TWO": out.get("TWO")})

    def test_every_chart_kind_draws(self):
        html = (SRC / "stage2.html").read_text()
        script = html.split("<script>")[-1].split("</script>")[0]
        out = self.node("""
          global.window=global; global.location={hash:''}; global.addEventListener=()=>{};
          global.document={getElementById:()=>({style:{}})}; global.module={exports:{}};
          eval(%s);
          const c=module.exports.chart;
          console.log(JSON.stringify([c({c:'bar',s:'Sales~1,5,3',x:'a,b,c'}),c({c:'big',s:'Sales~12000'}),
            c({c:'line',s:'A~1,,3;B~2,2,2',x:'x,y,z',t:'<b> & co'})]));
        """ % json.dumps(script))
        bar, big, line = out
        self.assertIn("b has the highest sales: 5", bar)
        self.assertIn("12K", big)
        self.assertIn("&lt;b&gt; &amp; co", line)
        for svg in out:
            self.assertNotIn("NaN", svg)

    def test_report_builder_makes_spoken_charts_and_data(self):
        box = Sandbox()
        self.addCleanup(box.close)
        r = subprocess.run(["python3", "-I", str(box.d / "gen_report.py")], capture_output=True,
                           text=True, env={"HOME": str(box.home), "PATH": "/usr/bin:/bin"}, cwd=box.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        made = [p for p in box.root.rglob("*.html") if p.name not in ("stage.html", "stage2.html")]
        self.assertTrue(made, r.stdout)
        text = made[0].read_text()
        self.assertGreater(text.count("<figure data-say="), 0)
        data = text.split("id='report-data'>" if "id='report-data'" in text else 'id="report-data">')[1]
        json.loads(data.split("</script>")[0])


if __name__ == "__main__":
    unittest.main()
