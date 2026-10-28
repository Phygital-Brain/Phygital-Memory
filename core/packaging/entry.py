"""PyInstaller entry for the Phygital Memory server. Adds a non-interactive `create` (password lines from stdin)."""
import getpass
import sys

if not sys.stdin.isatty():
    getpass.getpass = lambda prompt="": sys.stdin.readline().rstrip("\r\n")

from phygital_memory.server import main

if __name__ == "__main__":
    main()
