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

Routing also establishes an action boundary. Read-only inspection can proceed
without approval. Requests to edit, install, rebuild, restart, commit, or
otherwise change the machine are marked as changes, escalated to the smart lane,
and stopped at a visible confirmation gate. Destructive requests receive a
stronger protected-change classification. GHOST does not yet execute these
plans; this boundary is the contract the future tool runner must enforce.

The first tool runner is read-only and strictly whitelisted:

```bash
ghost inspect health
ghost inspect services
ghost inspect processes
ghost inspect config
```

Smart voice investigations automatically attach relevant results from these
tools for service, performance, process, and Nix configuration questions. The
runner accepts inspection targets rather than arbitrary shell commands and has
no mutation path.

Change requests use the smart model to create a proposal containing scope,
ordered steps, risks, validation, and rollback. The newest proposal is stored
privately under GHOST's state directory with `pending-review` status:

```bash
ghost propose "install a Nix package for this machine"
ghost proposal
```

Voice change requests use the same proposal path automatically. Saving a
proposal does not approve or execute it.

Before routing, voice normalizes a small audited vocabulary of common local
speech errors, including `h-top` to `htop` and `configuration.next` to
`configuration.nix`, and prints any correction. Package additions receive a
read-only nixpkgs availability check. Proposals missing required safety sections,
containing unresolved placeholders, known speech artifacts, or unsupported
validation commands are rejected rather than saved. Voice speaks only a short
pending-review summary; the complete proposal remains visible in the terminal
and through `ghost proposal`.

Approval is a separate non-executing state transition. It requires the exact
proposal ID, refuses protected changes, verifies that tracked Nix configuration
files have not changed, and issues a random token bound to the proposal digest.
Tokens expire after 15 minutes by default, and only their SHA-256 hashes are
stored in the private proposal state and append-only approval audit:

```bash
ghost proposal
ghost approve <proposal-id>
```

Approval never runs a command or edits a file.
The raw credential is kept in a private mode-0600 state file for internal
verification, so the user never needs to copy, remember, or repeat it.

The first production executor supports exactly one operation: adding a verified
top-level nixpkgs package to `environment.systemPackages` in the known
`~/.config/nixos/configuration.nix` target. It verifies approval, challenge,
digest, expiry, credential, and machine fingerprints; creates a private backup;
parses the edited Nix file; restores the exact original bytes and mode on
validation failure; records an audit event; prints the diff; and contains no
rebuild operation. Explicit fixture-test mode remains restricted to `/tmp`.

`ghost shadow [package]` copies the actual Nix configuration and GHOST module
into an isolated directory beneath `/tmp`, runs the full approved fixture edit,
then forces validation failure on a fresh clone and verifies exact rollback. It
hashes and checks the modes of the source files before and after the run and
removes the temporary workspace when finished.

Execution authorization uses a second deliberate, short-lived gate:

```text
ghost execute <proposal-id>
ghost authorize execution <proposal-id>
```

The first command issues a two-minute challenge after rechecking approval,
digest, credential, expiry, and machine fingerprints. The second command must
match exactly; casual confirmation is ignored. Voice accepts only the exact
phrases `execute approved proposal <id>` and `authorize execution <id>`. Passing
the challenge invokes only the narrow package editor described above. It stops
after syntax validation with status `executed-awaiting-activation`; full
evaluation and activation remain separate gates.

The normal voice flow hides proposal IDs and combines approval with challenge
issuance while preserving those internal state transitions:

```text
request a package change
stage this proposal
authorize package edit
```

`stage this proposal` targets only the active pending proposal, approves it, and
issues the short-lived challenge. `authorize package edit` resolves that private
challenge and invokes the narrow editor. Casual confirmations such as yes, yeah,
sure, or do it do not match either command. The ID-based commands remain
available for inspection and recovery.

After an authorized edit, GHOST automatically verifies the recorded post-edit
hash and trusted backup, parses the file, and evaluates the complete NixOS
system with `nix-instantiate`. Evaluation produces a derivation but does not
build or activate it. Failure restores the original file and mode; success moves
the proposal to `validated-awaiting-activation`. `ghost verify <id>` exposes the
same gate for recovery and diagnostics.

Successful evaluation automatically prepares a separate two-minute system
activation challenge. Only the exact phrase `authorize system activation`
consumes it; casual confirmation is ignored. The activation state machine tracks
the generation before and after the switch and records the rebuild exit status
and a private log. Before running, it rechecks the consumed challenge, expiry,
successful evaluation, and both validated file fingerprints. It targets only
the exact configured NixOS files and runs one fixed command through normal
interactive sudo authentication. Success additionally requires a new generation
and agreement between the system profile and `/run/current-system`. Failure or
ambiguous state is reported without claiming success. GHOST retains the
pre-switch generation and reports the explicit NixOS rollback command.

Fixture activation is confined to `/tmp`; the test suite exercises successful
and failed activation without invoking sudo or changing the live system.

The latest successful activation can be recovered without remembering proposal
IDs or Nix commands:

```text
prepare system rollback
authorize system rollback
```

Preparation is read-only. It binds a two-minute challenge to the latest
activated proposal, the recorded before/after generations, the unchanged edited
configuration, and the trusted pre-edit backup. Exact authorization restores
that backup byte-for-byte with its original mode, then runs the fixed NixOS
rollback command through normal sudo authentication. Success requires the
recorded previous generation and active system profile to agree. Casual
confirmation is ignored, and fixture rollback is restricted to `/tmp`.
