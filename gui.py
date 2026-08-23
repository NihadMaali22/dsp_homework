#!/usr/bin/env python3
"""
DSP Interactive Studio - GUI Launcher
Starts the interactive Web UI and automatically launches the user's default browser.
"""

import sys
import os
import socket
import threading
import time
import webbrowser
import argparse

# Color terminal formatting
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def find_free_port(starting_port=5000, max_attempts=50):
    """Find a free TCP port starting from starting_port."""
    for port in range(starting_port, starting_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return starting_port


def print_banner(url):
    print(f"\n{CYAN}{BOLD}" + "=" * 68)
    print("  🚀  DIGITAL SIGNAL PROCESSING (DSP) INTERACTIVE STUDIO")
    print("      Discrete-Time Singularity, Convolution & DTFT Analysis")
    print("=" * 68 + f"{RESET}\n")
    print(f" {GREEN}✔  Interactive Web GUI is up and running!{RESET}")
    print(f" {BOLD}👉  Open in your web browser:{RESET}  {CYAN}{BOLD}{url}{RESET}\n")
    print(f" {YELLOW}💡  Features:{RESET}")
    print("   • Part I: Interactive Singularity Signals Generator & Live Audio")
    print("   • Part II: 3x2 Convolution & DTFT Analysis Matrix (with Theorem Check)")
    print("   • Part III: Step-by-Step Flip & Shift Convolution Animator")
    print("   • Part IV: Custom Arbitrary Signals & Expression Evaluator")
    print("   • 1-Click Homework Presets & High-Res Figure Export\n")
    print(f" {BOLD}Press Ctrl+C in this terminal to stop the server.{RESET}")
    print(f"{CYAN}" + "=" * 68 + f"{RESET}\n")


def open_browser(url, delay_sec=1.0):
    """Open web browser in a background thread."""
    def _open():
        time.sleep(delay_sec)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    t = threading.Thread(target=_open, daemon=True)
    t.start()


def main():
    parser = argparse.ArgumentParser(description="DSP Interactive GUI Launcher")
    parser.add_argument("--port", "-p", type=int, default=None, help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host binding (default: 127.0.0.1)")
    parser.add_argument("--no-browser", "-n", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    port = args.port or find_free_port(5000)
    url = f"http://{args.host}:{port}"

    print_banner(url)

    if not args.no_browser:
        open_browser(url)

    from app import app
    # Suppress werkzeug debug clutter in standard launch mode
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    app.run(host=args.host, port=port, debug=False)


if __name__ == "__main__":
    main()
