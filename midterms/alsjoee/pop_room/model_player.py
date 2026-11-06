"""A Gemini player for Prince of Persia: One Room.

The player sees only what a human player sees: the rules text from the play
intro, the current observation, the legal actions and, optionally, its own
last N (action, result) pairs. With view="local" it also gets one line naming
the tiles next to the Prince, worked out from the observed map alone. It
returns one action string; the episode
decides whether it is accepted. It never touches the World.

The model client is any callable client(prompt, seed) -> ModelReply that may
raise. VertexClient calls Gemini the same way course_game/narrator.py does;
tests pass a fake client instead.
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
import json
import os
import re
import time

from .episode import PLAYER_ID
from .rules_text import intro, render
from .world import EMPTY, EXIT, FLOOR, GATE, PLATE, SPIKES, START, WALL

DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_MODEL_CALLS = 60
TIMEOUT_S = 30.0
EPISODE_TIME_LIMIT_S = 600.0
LIMIT_REASON = "model-call limit"
TIME_LIMIT_REASON = "time limit"
MAX_CONSECUTIVE_FAILURES = 5
UNAVAILABLE_REASON = "model unavailable"
FALLBACK_MOVE = "wait (fallback: model call failed)"  # how a fallback appears in the model's history
VIEWS = ("map", "local")
TILE_NAMES = {FLOOR: "floor", START: "floor", EMPTY: "gap", SPIKES: "spikes", PLATE: "plate",
              GATE: "gate", WALL: "wall", EXIT: "exit"}

ACTION_WORDS = re.compile(r"\b(jump[ _-]?left|jump[ _-]?right|left|right|climb|wait)\b")


@dataclass(frozen=True)
class ModelReply:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None   # includes thinking_tokens, which are billed as output
    model_version: str | None = None
    thinking_tokens: int | None = None


class ModelConfigError(ValueError):
    """The environment is not configured for a live call."""


def vertex_settings():
    """Project, location and model from the environment; no call is made."""
    settings = {
        "project": os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip(),
        "location": os.environ.get("GOOGLE_CLOUD_LOCATION", "").strip(),
        "model": os.environ.get("COURSE_MODEL", "").strip() or DEFAULT_MODEL,
    }
    missing = [name for name, key in (("GOOGLE_CLOUD_PROJECT", "project"),
                                      ("GOOGLE_CLOUD_LOCATION", "location")) if not settings[key]]
    if missing:
        raise ModelConfigError("Configure " + ", ".join(missing) + " using the course instructions.")
    return settings


class VertexClient:
    """One Gemini call per prompt on Vertex AI, with no retries and no tools."""

    def __init__(self, project, location, model, timeout_s=TIMEOUT_S):
        self.project, self.location, self.model = project, location, model
        self.timeout_s = timeout_s

    def __call__(self, prompt, seed=None):
        from google import genai
        from google.genai import types

        with genai.Client(
            vertexai=True, project=self.project, location=self.location,
            http_options=types.HttpOptions(
                timeout=int(self.timeout_s * 1000), retry_options=types.HttpRetryOptions(attempts=1)
            ),
        ) as client:
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                    seed=seed,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
        return reply_from_response(response, self.model)


def reply_from_response(response, model):
    """A ModelReply from a Gemini response. Thinking tokens are billed as output,
    so they are added to output_tokens and also kept as thinking_tokens."""
    usage = response.usage_metadata
    thinking = (getattr(usage, "thoughts_token_count", None) or 0) if usage is not None else None
    candidates = getattr(usage, "candidates_token_count", None)
    output = None
    if candidates is not None or thinking:
        output = (candidates or 0) + thinking
    return ModelReply(
        text=response.text or "",
        input_tokens=getattr(usage, "prompt_token_count", None),
        output_tokens=output,
        model_version=response.model_version or model,
        thinking_tokens=thinking,
    )


def parse_action(reply, legal_actions):
    """The first legal action named in the reply, or None."""
    for match in ACTION_WORDS.finditer(reply.lower()):
        word = match.group(1)
        if word.startswith("jump"):
            word = "jump_" + ("left" if word.endswith("left") else "right")
        if word in legal_actions:
            return word
    return None


def _tile(grid, row, col):
    if 0 <= row < len(grid) and 0 <= col < len(grid[row]):
        return grid[row][col]
    return None


def _name(tile, gate):
    if tile is None:
        return "edge of map"
    if tile == GATE:
        return f"gate ({gate})"
    return TILE_NAMES.get(tile, f"unknown tile {tile!r}")


def _below_gap(grid, row, col):
    """What a Prince stepping into the gap at (row, col) would land on, by the observed map."""
    fallen = 0
    while _tile(grid, row, col) == EMPTY:
        if _tile(grid, row + 1, col) == WALL:  # walls are solid: the fall stops above one
            drop = f", fall {fallen} floor{'s' if fallen > 1 else ''}" if fallen else ""
            return f"wall; you would stop on top of it{drop}"
        row, fallen = row + 1, fallen + 1
    tile = _tile(grid, row, col)
    if tile is None:
        return "nothing; you would fall off the map"
    name = TILE_NAMES.get(tile, f"unknown tile {tile!r}")
    return f"{name}, fall {fallen} floor{'s' if fallen > 1 else ''}"


def local_view(observation):
    """One line naming the tiles left, right, above and below the Prince.

    Uses only the observation's map, position and gate state. For a gap on the
    left or right it also says what lies below it, since walking there means falling.
    """
    grid, gate = observation["map"], observation["gate"]
    row, col = observation["prince"]["row"], observation["prince"]["col"]
    parts = []
    for side, (r, c) in (("left", (row, col - 1)), ("right", (row, col + 1)),
                         ("above", (row - 1, col)), ("below", (row + 1, col))):
        tile = _tile(grid, r, c)
        text = _name(tile, gate)
        if tile == EMPTY and side in ("left", "right"):
            text += f" (below it: {_below_gap(grid, r, c)})"
        parts.append(f"{side} = {text}")
    return "Next to you: " + "; ".join(parts)


def build_prompt(observation, legal_actions, history, max_steps, view="map"):
    """Everything the model sees: rules, observation, legal actions, own history."""
    if view not in VIEWS:
        raise ValueError(f"view must be one of {VIEWS}")
    parts = [
        intro(max_steps),
        "",
        "Current map (@ is you):",
        render(observation),
    ]
    if view == "local":
        parts.append(local_view(observation))
    parts += [
        "",
        "Observation:",
        json.dumps(observation),
        "",
        "Legal actions: " + ", ".join(legal_actions),
    ]
    if history:
        parts += ["", f"Your last {len(history)} moves (oldest first):"]
        parts += [f"- {action}: {result}" for action, result in history]
    parts += ["", "Reply with exactly one word: one of the legal actions."]
    return "\n".join(parts)


class ModelPlayer:
    def __init__(self, client, history=0, max_model_calls=MAX_MODEL_CALLS,
                 timeout_s=TIMEOUT_S, max_steps=40, seed=None, view="map",
                 time_limit_s=EPISODE_TIME_LIMIT_S):
        if history < 0:
            raise ValueError("history must be 0 or more")
        if view not in VIEWS:
            raise ValueError(f"view must be one of {VIEWS}")
        self.view = view
        self.client = client
        self.history = history
        self.max_model_calls = max_model_calls
        self.timeout_s = timeout_s
        self.time_limit_s = time_limit_s
        self.max_steps = max_steps
        self.seed = seed
        self.reset()

    def reset(self):
        self.model_calls = 0
        self.memory = []

    @property
    def budget_left(self):
        return self.max_model_calls - self.model_calls

    def recent(self):
        return self.memory[-self.history:] if self.history else []

    def choose(self, observation, legal_actions):
        """Ask the model once. Returns the action to submit and what happened."""
        prompt = build_prompt(observation, legal_actions, self.recent(), self.max_steps, self.view)
        self.model_calls += 1
        started = time.monotonic()
        # A fresh thread per call: a hung call is abandoned, not waited on.
        pool = ThreadPoolExecutor(max_workers=1)
        try:
            reply = pool.submit(self.client, prompt, self.seed).result(timeout=self.timeout_s)
            error = None
        except FutureTimeout:
            reply, error = None, f"timed out after {self.timeout_s:g} s"
        except Exception as exc:  # any client failure becomes a labelled fallback
            reply, error = None, f"{type(exc).__name__}: {exc}"
        finally:
            pool.shutdown(wait=False)
        latency = time.monotonic() - started

        if reply is None:
            return {"prompt": prompt, "action": "wait", "raw_reply": None, "parsed_action": None, "fallback": True,
                    "error": error, "latency_s": latency, "input_tokens": None,
                    "output_tokens": None, "thinking_tokens": None, "model_version": None}
        parsed = parse_action(reply.text, legal_actions)
        return {
            "prompt": prompt,
            # No legal action named: submit the reply as given, so it counts as invalid.
            "action": parsed if parsed is not None else reply.text,
            "raw_reply": reply.text, "parsed_action": parsed, "fallback": False, "error": None,
            "latency_s": latency, "input_tokens": reply.input_tokens,
            "output_tokens": reply.output_tokens, "thinking_tokens": reply.thinking_tokens,
            "model_version": reply.model_version,
        }

    def remember(self, action, result_text):
        self.memory.append((action, result_text))


def run_episode(episode, player, room, seed, on_step=None):
    """Play one episode. Returns (step records, outcome).

    The time limit is checked between moves, so a call already under way can
    run past it by up to the per-call timeout.
    """
    observation = episode.reset(seed=seed, room=room)
    player.reset()
    records = []
    stopped = None
    failures_in_a_row = 0
    started = time.monotonic()
    while episode.outcome()["status"] != "terminal":
        if failures_in_a_row >= MAX_CONSECUTIVE_FAILURES:
            stopped = UNAVAILABLE_REASON
            break
        if player.budget_left <= 0:
            stopped = LIMIT_REASON
            break
        if time.monotonic() - started >= player.time_limit_s:
            stopped = TIME_LIMIT_REASON
            break
        legal = episode.legal_actions(PLAYER_ID)
        choice = player.choose(observation, legal)
        failures_in_a_row = failures_in_a_row + 1 if choice["fallback"] else 0
        result = episode.step(PLAYER_ID, choice["action"])
        player.remember(FALLBACK_MOVE if choice["fallback"] else choice["action"], result["text"])
        record = {"type": "step", "step": episode.steps, "observation": observation,
                  "legal_actions": legal, **choice,
                  "accepted": result["accepted"], "result": result["text"]}
        records.append(record)
        if on_step:
            on_step(record)
        observation = result["observation"]
    outcome = episode.outcome()
    if stopped:
        outcome = {**outcome, "status": "terminal", "reason": stopped, "score": 0}
    return records, outcome


def summarize(records, outcome, player, *, model, room, seed, git_commit):
    def total(key):
        return sum(r.get(key) or 0 for r in records)

    fallbacks = sum(r["fallback"] for r in records)
    versions = sorted({r["model_version"] for r in records if r["model_version"]})
    return {
        "type": "summary",
        "outcome": outcome["reason"], "score": outcome["score"],
        "steps": outcome["steps"], "invalid_actions": outcome["invalid_actions"],
        "fallbacks": fallbacks,
        "model_calls": player.model_calls,
        "model_moves": len(records) - fallbacks,
        "input_tokens": total("input_tokens"), "output_tokens": total("output_tokens"),
        "thinking_tokens": total("thinking_tokens"),
        "total_tokens": total("input_tokens") + total("output_tokens"),
        "total_latency_s": round(sum(r["latency_s"] for r in records), 3),
        "model": model, "model_versions": versions,
        "history": player.history, "view": player.view, "max_model_calls": player.max_model_calls,
        "time_limit_s": player.time_limit_s,
        "room": room, "seed": seed, "git_commit": git_commit,
    }
