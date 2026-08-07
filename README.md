# GHOST

GHOST is the personality layer of a lived-in NixOS cyberdeck.

It observes the workstation through small shell-based sensors, remembers the
machine it inhabits, and reports back with a concise hacker-workstation voice.
It is not an operating system or a general-purpose AI framework.

## Current state

- Bash runtime
- System, RAM/swap, desktop, network, storage, power, memory, and Nix sensors
- Local condition reporting for storage, battery, and system load
- Machine-specific memory
- Grounded model conversations through `ghost ask`
- Private conversation continuity and deliberate long-term memories
- Local push-to-talk, transcription, and spoken responses
- Global command through a user-local symlink

## Layout

```text
bin/ghost             command entry point
sensors/              small executable sensor modules
memory/machine.md     facts about this machine
config/personality.md GHOST's identity and voice
config/model.env.example model connection template
lib/context           live context assembly
lib/ask               model conversation bridge
```

## Run

```bash
./bin/ghost
```

To make the command available globally for the current user:

```bash
ln -s "$(pwd)/bin/ghost" ~/.local/bin/ghost
```

Each executable in `sensors/` owns one narrow view of the machine. The command
runner invokes sensors independently, so a missing or broken module does not
take the rest of GHOST offline.

## Conversation

GHOST can talk through any OpenAI-compatible chat-completions endpoint. Copy
the local configuration template and set the model exposed by your server:

```bash
cp config/model.env.example config/model.env
$EDITOR config/model.env
ghost ask "what is happening on this machine?"
```

The default URL targets an Ollama-compatible local endpoint. `config/model.env`
is ignored by Git because it may contain credentials. Use `ghost context` to
inspect the exact personality, memory, and live machine state supplied to the
model. Conversation currently requires `curl` and `jq`. On NixOS, GHOST first
reads declarative model settings from `/etc/ghost/model.env`; the repo-local
configuration remains an optional override.

Conversation state is stored privately under `~/.local/state/ghost`, never in
Git. GHOST supplies the most recent 12 messages to each request by default:

```bash
ghost history
ghost clear
ghost remember "Athena is archived, not an active project"
ghost memories
```

Clearing conversation history does not remove deliberate memories.

## Voice

The NixOS runtime module provides Whisper.cpp, Piper, pinned speech models, and
PipeWire tools. After activating that module:

```bash
ghost listen
ghost listen 6
ghost speak "system nominal"
ghost voice
ghost audio
```

With no duration, `ghost listen` and `ghost voice` record until ENTER is
pressed. Supplying seconds retains bounded capture. `ghost voice` transcribes locally, passes it
through the same context and conversation history as `ghost ask`, and speaks
the answer locally. The initial Piper voice is a reference voice intended for
testing; it is not GHOST's permanent voice identity. A specific PipeWire input
or output can be selected in ignored `config/voice.env` using the node names or
IDs shown by `ghost audio`.

Voice mode reports capture, transcription, model, synthesis, and playback
timings. It uses the faster non-thinking `qwen3:4b-instruct`, a smaller
128-token response budget, six recent messages, and a compact live context by
default. Terminal conversation retains `qwen3:8b`, its full machine context,
and larger settings. Use `ghost benchmark` for a repeatable local model
throughput measurement before and after runtime or acceleration changes. Pass
a model name to compare lanes:

```bash
ghost benchmark qwen3:4b-instruct
ghost benchmark qwen3:8b
```

Voice routing is automatic. Greetings, simple questions, and machine lookups use
the fast lane. Diagnosis, configuration changes, coding, planning, and deeper
reasoning escalate to the smart lane with full context. GHOST prints the selected
route before answering. Inspect routing without recording audio using
`ghost route <request>`, or set `GHOST_VOICE_ROUTE=fast` or `smart` in the ignored
`config/voice.env` to force a lane temporarily.
