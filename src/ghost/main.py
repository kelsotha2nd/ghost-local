#!/usr/bin/env python3


BANNER = r"""
╭────────────────────╮
│       GHOST        │
│ Local Intelligence │
│ Runtime v0.1        │
╰────────────────────╯
"""


def main():
    print(BANNER)

    while True:
        try:
            command = input("\n[GHOST] > ")

            if command.lower() in ["exit", "quit"]:
                print("GHOST offline.")
                break

            print(f"Received: {command}")

        except KeyboardInterrupt:
            print("\nGHOST offline.")
            break


if __name__ == "__main__":
    main()