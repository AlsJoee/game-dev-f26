"""Evaluation runner tests with a fake model client. No network, no credits."""

import csv
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from pop_room import __main__ as cli
from pop_room import evaluate as ev
from pop_room.model_player import ModelReply

MODEL = "gemini-3.5-flash-lite"
ROOM_A_SOLUTION = ["right", "jump_right", "right", "right", "right", "right", "right"]
PRICES = {MODEL: {"input_usd_per_1m": 0.5, "output_usd_per_1m": 2.0,
                  "source": "https://example.test/prices", "checked": "2026-11-01"}}


class SolvingClient:
    """Plays room A's solution, 100 input and 4 output tokens per call."""

    def __init__(self):
        self.calls = 0

    def __call__(self, prompt, seed=None):
        self.calls += 1
        legal = prompt.split("Legal actions: ")[1].split("\n")[0].split(", ")
        for action in ROOM_A_SOLUTION:
            if action in legal and not (action == "right" and "jump_right" in legal):
                return ModelReply(action, input_tokens=100, output_tokens=4, model_version="fake")
        return ModelReply("wait", input_tokens=100, output_tokens=4, model_version="fake")


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def evaluate(self, client=None, prices=PRICES, histories=(0, 5), trials=2):
        return ev.run_evaluation(["A"], trials, list(histories), client or SolvingClient(),
                                 model=MODEL, commit="abc123", prices=prices, today="2026-11-02",
                                 traces_dir=self.tmp / "traces")


class CostTest(unittest.TestCase):
    def test_cost_from_prices(self):
        price = ev.price_for(PRICES, MODEL)
        self.assertEqual(price, (0.5, 2.0))
        self.assertEqual(ev.est_cost(1_000_000, 500_000, price), 1.5)
        self.assertEqual(ev.est_cost(700, 28, price), 0.000406)

    def test_missing_prices_are_unknown(self):
        placeholder = {MODEL: {"input_usd_per_1m": None, "output_usd_per_1m": None}}
        for prices in ({}, placeholder, {MODEL: {"input_usd_per_1m": 0.5}}):
            with self.subTest(prices=prices):
                self.assertIsNone(ev.price_for(prices, MODEL))
                self.assertEqual(ev.est_cost(700, 28, ev.price_for(prices, MODEL)), "unknown")
        self.assertEqual(ev.est_cost(None, 28, (0.5, 2.0)), "unknown")

    def test_placeholder_prices_file_gives_unknown(self):
        placeholder = {MODEL: {"input_usd_per_1m": None, "output_usd_per_1m": None,
                               "source": "https://example.test/prices", "checked": None}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prices.json"
            path.write_text(json.dumps(placeholder))
            prices = ev.load_prices(path)
        self.assertIsNone(ev.price_for(prices, MODEL))
        self.assertEqual(ev.est_cost(700, 28, ev.price_for(prices, MODEL)), "unknown")

    def test_shipped_prices(self):
        self.assertEqual(ev.price_for(ev.load_prices(), MODEL), (0.30, 2.50))


class RunAndCsvTest(TempDirTest):
    def test_one_bfs_and_one_model_row_per_history_per_seed(self):
        rows = self.evaluate()
        self.assertEqual([(r["player"], r["history"], r["seed"]) for r in rows],
                         [("bfs", "", 1), ("model", 0, 1), ("model", 5, 1),
                          ("bfs", "", 2), ("model", 0, 2), ("model", 5, 2)])
        model = rows[1]
        self.assertEqual((model["outcome"], model["score"], model["steps"], model["model_calls"]),
                         ("reached the exit", 1, 7, 7))
        self.assertEqual((model["input_tokens"], model["output_tokens"]), (700, 28))
        self.assertEqual(model["est_cost_usd"], 0.000406)
        self.assertEqual((rows[0]["model"], rows[0]["est_cost_usd"]), ("", 0.0))

    def test_model_traces_written(self):
        self.evaluate()
        names = sorted(p.name for p in (self.tmp / "traces").iterdir())
        self.assertEqual(names, [f"A-seed{s}-h{h}-{MODEL}.jsonl" for s in (1, 2) for h in (0, 5)])
        last = json.loads((self.tmp / "traces" / names[0]).read_text().splitlines()[-1])
        self.assertEqual((last["type"], last["git_commit"]), ("summary", "abc123"))

    def test_existing_trace_refused_before_any_call(self):
        (self.tmp / "traces").mkdir()
        ev.trace_path("A", 2, 5, MODEL, self.tmp / "traces").write_text("old")
        client = SolvingClient()
        with self.assertRaises(FileExistsError):
            self.evaluate(client)
        self.assertEqual(client.calls, 0)

    def test_csv_columns_and_append(self):
        path = self.tmp / "results" / "results.csv"
        ev.append_csv(path, self.evaluate(histories=(0,), trials=1))
        ev.append_csv(path, self.evaluate(histories=(5,), trials=1))
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(reader.fieldnames, [
            "date", "git_commit", "player", "model", "view", "history", "room", "seed", "outcome",
            "score", "steps", "invalid_actions", "fallbacks", "model_calls", "input_tokens",
            "output_tokens", "total_latency_s", "est_cost_usd"])
        self.assertEqual(len(rows), 4)  # one header, four rows from two runs
        self.assertEqual((rows[1]["player"], rows[1]["model"], rows[1]["est_cost_usd"]),
                         ("model", MODEL, "0.000406"))

    def test_unknown_cost_in_csv(self):
        path = self.tmp / "results.csv"
        ev.append_csv(path, self.evaluate(prices={}, histories=(0,), trials=1))
        with path.open(newline="") as f:
            self.assertEqual(list(csv.DictReader(f))[1]["est_cost_usd"], "unknown")

    def test_view_in_rows_traces_and_names(self):
        rows = self.evaluate(histories=(0,), trials=1)
        self.assertEqual([(r["player"], r["view"]) for r in rows], [("bfs", ""), ("model", "map")])
        rows = ev.run_evaluation(["A"], 1, [0], SolvingClient(), model=MODEL, commit="abc123",
                                 prices=PRICES, today="2026-11-02", traces_dir=self.tmp / "traces",
                                 view="local")
        self.assertEqual(rows[1]["view"], "local")
        names = sorted(p.name for p in (self.tmp / "traces").iterdir())
        self.assertEqual(names, [f"A-seed1-h0-{MODEL}.jsonl", f"A-seed1-h0-local-{MODEL}.jsonl"])
        lines = (self.tmp / "traces" / names[1]).read_text().splitlines()
        self.assertEqual(json.loads(lines[-1])["view"], "local")
        self.assertIn("Next to you:", json.loads(lines[0])["prompt"])
        self.assertNotIn("Next to you:", json.loads(
            (self.tmp / "traces" / names[0]).read_text().splitlines()[0])["prompt"])

    def test_results_file_from_before_view_is_upgraded(self):
        path = self.tmp / "results.csv"
        old = ev.COLUMNS_BEFORE_VIEW
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=old)
            writer.writeheader()
            for row in self.evaluate(histories=(0,), trials=1):
                writer.writerow({k: row[k] for k in old})
        ev.append_csv(path, ev.run_evaluation(
            ["A"], 1, [0], SolvingClient(), model=MODEL, commit="abc123", prices=PRICES,
            today="2026-11-02", traces_dir=self.tmp / "traces", view="local"))
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(reader.fieldnames, ev.COLUMNS)
        self.assertEqual([(r["player"], r["view"]) for r in rows],
                         [("bfs", ""), ("model", "map"), ("bfs", ""), ("model", "local")])

    def test_csv_with_other_columns_is_not_appended(self):
        path = self.tmp / "results.csv"
        path.write_text("date,score\n2026-10-01,1\n")
        with self.assertRaises(ValueError):
            ev.append_csv(path, self.evaluate(histories=(0,), trials=1))


class SummaryTest(TempDirTest):
    def test_summary_table(self):
        rows = self.evaluate()
        rows[2]["est_cost_usd"] = "unknown"  # one unknown cost makes its group unknown
        text = ev.summary_markdown(rows, today="2026-11-02", model=MODEL, commit="abc123",
                                   source=ev.price_source(PRICES, MODEL))
        for line in ("- Date: 2026-11-02", f"- Model: {MODEL}", "- Commit: abc123",
                     "- Price source: https://example.test/prices (checked 2026-11-01)"):
            self.assertIn(line, text)
        table = [line for line in text.splitlines() if line.startswith("| ") and "---" not in line]
        self.assertEqual(table[1:], [
            "| bfs | - | - | A | 2/2 | 7.0 | 0 | 0 | 0.00 | 0 | 0.000000 |",
            "| model | map | 0 | A | 2/2 | 7.0 | 0 | 0 | 0.00 | 1456 | 0.000812 |",
            "| model | map | 5 | A | 2/2 | 7.0 | 0 | 0 | 0.00 | 1456 | unknown |",
        ])

    def test_summary_groups_by_view(self):
        rows = self.evaluate(histories=(0,), trials=1)
        rows += [r for r in ev.run_evaluation(
            ["A"], 1, [0], SolvingClient(), model=MODEL, commit="abc123", prices=PRICES,
            today="2026-11-02", traces_dir=self.tmp / "traces", view="local") if r["player"] == "model"]
        text = ev.summary_markdown(rows, today="2026-11-02", model=MODEL, commit="abc123", source="x")
        self.assertIn("| Player | View | History | Room |", text)
        views = [line.split(" | ")[1] for line in text.splitlines() if line.startswith("| model")]
        self.assertEqual(views, ["local", "map"])

    def test_price_source_says_when_prices_are_missing(self):
        self.assertIn("unknown", ev.price_source({}, MODEL))


class DirtyTreeTest(TempDirTest):
    def test_require_clean(self):
        with self.assertRaises(ev.DirtyTreeError):
            ev.require_clean("abc", True, allow_dirty=False)
        self.assertEqual(ev.require_clean("abc", True, allow_dirty=True), "abc-dirty")
        self.assertEqual(ev.require_clean("abc", False, allow_dirty=False), "abc")

    def test_own_outputs_do_not_make_the_tree_dirty(self):
        def fake_git(status):
            answers = {"rev-parse HEAD": "abc\n", "rev-parse --show-prefix": "midterms/alsjoee/\n",
                       "status --porcelain": status}
            return lambda *args: answers[" ".join(args)]

        outputs = "?? midterms/alsjoee/traces/\n M midterms/alsjoee/results/results.csv\n"
        with mock.patch.object(ev, "_git", fake_git(outputs)):
            self.assertEqual(ev.git_state(), ("abc", False))
        with mock.patch.object(ev, "_git", fake_git(outputs + " M midterms/alsjoee/pop_room/world.py\n")):
            self.assertEqual(ev.git_state(), ("abc", True))

    def run_cli(self, *extra, dirty):
        env = {"GOOGLE_CLOUD_PROJECT": "fake-project", "GOOGLE_CLOUD_LOCATION": "global",
               "COURSE_MODEL": MODEL}
        with mock.patch.dict(os.environ, env), \
             mock.patch.object(ev, "git_state", return_value=("abc", dirty)), \
             mock.patch.object(ev, "RESULTS", self.tmp / "results"), \
             mock.patch.object(ev, "TRACES", self.tmp / "traces"), \
             mock.patch.object(ev, "load_prices", return_value=PRICES), \
             mock.patch.object(cli.mp, "VertexClient", return_value=SolvingClient()), \
             mock.patch("builtins.print"):
            cli.main(["evaluate", "--rooms", "A", "--trials", "1", "--history", "0", *extra])

    def test_dirty_tree_refused_before_any_call(self):
        with self.assertRaises(SystemExit) as stop:
            self.run_cli(dirty=True)
        self.assertIn("uncommitted changes", str(stop.exception))
        self.assertFalse((self.tmp / "results").exists())
        self.assertFalse((self.tmp / "traces").exists())

    def test_allow_dirty_marks_rows(self):
        self.run_cli("--allow-dirty", dirty=True)
        with (self.tmp / "results" / "results.csv").open(newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual({r["git_commit"] for r in rows}, {"abc-dirty"})
        self.assertIn("- Commit: abc-dirty", (self.tmp / "results" / "summary.md").read_text())


if __name__ == "__main__":
    unittest.main()
