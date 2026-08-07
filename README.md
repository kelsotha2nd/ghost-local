# GHOST

GHOST is the personality layer of a lived-in NixOS cyberdeck.

It observes the workstation through small shell-based sensors, remembers the
machine it inhabits, and reports back with a concise hacker-workstation voice.
It is not an operating system or a general-purpose AI framework.

## Current state

- Bash runtime
- System, desktop, power, memory, and Nix sensors
- Machine-specific memory
- Global command through a user-local symlink

## Layout

```text
bin/ghost             command entry point
sensors/              small executable sensor modules
memory/machine.md     facts about this machine
config/personality.md GHOST's identity and voice
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
