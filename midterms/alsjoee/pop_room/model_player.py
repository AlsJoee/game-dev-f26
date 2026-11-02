"""A Gemini player for Prince of Persia: One Room.

The player sees only what a human player sees: the rules text from the play
intro, the current observation, the legal actions and, optionally, its own
last N (action, result) pairs. It returns one action string; the episode
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

DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_MODEL_CALLS = 60
TIMEOUT_S = 30.0
LIMIT_REASON = "model-call limit"

ACTION_WORDS = re.compile(r"\b(jump[ _-]?left|jump[ _-]?right|left|right|climb|wait)\b")


@dataclass(frozen=True)
class ModelReply:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    model_version: str | None = None


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
        usage = response.usage_metadata
        # Thinking tokens are billed as output, so they are counted as output here.
        output = None
        if usage is not None and usage.candidates_token_count is not None:
            output = usage.candidates_token_count + (usage.thoughts_token_count or 0)
        return ModelReply(
            text=response.text or "",
            input_tokens=getattr(usage, "prompt_token_count", None),
            output_tokens=output,
            model_version=response.model_version or self.model,
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


def build_prompt(observation, legal_actions, history, max_steps):
    """Everything the model sees: rules, observation, legal actions, own history."""
    parts = [
        intro(max_steps),
        "",
        "Current map (@ is you):",
        render(observation),
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
                 timeout_s=TIMEOUT_S, max_steps=40, seed=None):
        if history < 0:
            raise ValueError("history must be 0 or more")
        self.client = client
        self.history = history
        self.max_model_calls = max_model_calls
        self.timeout_s = timeout_s
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
        prompt = build_prompt(observation, legal_actions, self.recent(), self.max_steps)
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
                    "output_tokens": None, "model_version": None}
        parsed = parse_action(reply.text, legal_actions)
        return {
            "prompt": prompt,
            # No legal action named: submit the reply as given, so it counts as invalid.
            "action": parsed if parsed is not None else reply.text,
            "raw_reply": reply.text, "parsed_action": parsed, "fallback": False, "error": None,
            "latency_s": latency, "input_tokens": reply.input_tokens,
            "output_tokens": reply.output_tokens, "model_version": reply.model_version,
        }

    def remember(self, action, result_text):
        self.memory.append((action, result_text))


def run_episode(episode, player, room, seed, on_step=None):
    """Play one episode. Returns (step records, outcome)."""
    observation = episode.reset(seed=seed, room=room)
    player.reset()
    records = []
    stopped = False
    while episode.outcome()["status"] != "terminal":
        if player.budget_left <= 0:
            stopped = True
            break
        legal = episode.legal_actions(PLAYER_ID)
        choice = player.choose(observation, legal)
        result = episode.step(PLAYER_ID, choice["action"])
        player.remember(choice["action"], result["text"])
        record = {"type": "step", "step": episode.steps, "observation": observation,
                  "legal_actions": legal, **choice,
                  "accepted": result["accepted"], "result": result["text"]}
        records.append(record)
        if on_step:
            on_step(record)
        observation = result["observation"]
    outcome = episode.outcome()
    if stopped:
        outcome = {**outcome, "status": "terminal", "reason": LIMIT_REASON, "score": 0}
    return records, outcome


def summarize(records, outcome, player, *, model, room, seed, git_commit):
    def total(key):
        return sum(r[key] or 0 for r in records)

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
        "total_tokens": total("input_tokens") + total("output_tokens"),
        "total_latency_s": round(sum(r["latency_s"] for r in records), 3),
        "model": model, "model_versions": versions,
        "history": player.history, "max_model_calls": player.max_model_calls,
        "room": room, "seed": seed, "git_commit": git_commit,
    }
