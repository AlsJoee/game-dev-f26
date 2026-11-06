"""The --show flag on the baseline and model commands. No network, no credits."""

import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from pop_room import __main__ as cli
from pop_room import evaluate as ev
from pop_room.model_player import ModelReply


def run(*argv):
    """(printed text, delays passed to sleep) for one command."""
    out = io.StringIO()
    with mock.patch("time.sleep") as sleep, contextlib.redirect_stdout(out):
        cli.main(list(argv))
    return out.getvalue(), [call.args[0] for call in sleep.call_args_list]


class BaselineShowTest(unittest.TestCase):
    def test_show_prints_the_map_action_and_result_after_every_move(self):
        printed, _ = run("baseline", "--room", "A", "--show")
        self.assertIn("\n.@ .P.G.E\n 1. right: right\n", printed)
        self.assertIn("\n.. .P.G.@\n 7. right: right; reached the exit\n", printed)
        self.assertEqual(printed.count("@"), 7)

    def test_show_pauses_after_every_move_for_the_default_delay(self):
        _, delays = run("baseline", "--room", "A", "--show")
        self.assertEqual(delays, [0.8] * 7)

    def test_delay_sets_the_pause(self):
        _, delays = run("baseline", "--room", "A", "--show", "--delay", "0.25")
        self.assertEqual(delays, [0.25] * 7)

    def test_without_show_there_is_no_map_and_no_pause(self):
        printed, delays = run("baseline", "--room", "A")
        self.assertNotIn("@", printed)
        self.assertIn(" 1. right: right\n", printed)
        self.assertEqual(delays, [])

    def test_negative_delay_is_refused(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            run("baseline", "--room", "A", "--show", "--delay", "-1")


class ModelShowTest(unittest.TestCase):
    def run_model(self, *replies, extra=("--show",)):
        script = list(replies)

        def client(prompt, seed=None):
            item = script.pop(0)
            if isinstance(item, Exception):
                raise item
            return ModelReply(item)

        env = {"GOOGLE_CLOUD_PROJECT": "fake-project", "GOOGLE_CLOUD_LOCATION": "global",
               "COURSE_MODEL": "fake-model"}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, env), \
                mock.patch.object(ev, "TRACES", Path(tmp)), \
                mock.patch.object(ev, "git_state", return_value=("abc", False)), \
                mock.patch.object(cli.mp, "VertexClient", return_value=client):
            return run("model", "--room", "A", "--seed", "1", *extra)

    def test_show_prints_the_map_after_every_move(self):
        printed, delays = self.run_model("right", "wait", "no idea", RuntimeError("503"),
                                         "right", extra=("--show", "--delay", "0.5"))
        self.assertIn("\n.@ .P.G.E\n 1. right: right", printed)
        self.assertIn("\n.@ .P.G.E\n 2. wait: wait", printed)
        self.assertIn("\n.@ .P.G.E\n 3. invalid reply 'no idea':", printed)
        self.assertIn("\n.@ .P.G.E\n 4. wait (fallback: RuntimeError: 503):", printed)
        self.assertEqual(delays, [0.5] * 5)

    def test_show_survives_a_fall_off_the_map(self):
        printed, _ = self.run_model("right", "right")
        self.assertIn("\n.. .P.G.E\n 2. right: right; died: fell off the bottom", printed)
        self.assertIn("outcome: died: fell off the bottom", printed)

    def test_without_show_there_is_no_map_and_no_pause(self):
        printed, delays = self.run_model("right", "right", extra=())
        self.assertNotIn("@", printed)
        self.assertEqual(delays, [])


if __name__ == "__main__":
    unittest.main()
