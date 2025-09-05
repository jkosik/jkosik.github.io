#!/usr/bin/env python3
"""
Test various macOS commands that can be triggered by "go" detection.
This demonstrates different actions you can perform.
"""

import subprocess
import time

def test_command(description, command, safe=True):
    """Test a macOS command."""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {' '.join(command)}")

    if not safe:
        response = input("This command might open something. Continue? (y/N): ")
        if response.lower() != 'y':
            print("⏭️  Skipped")
            return

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ Success! Output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("macOS Voice Command Test")
    print("=" * 40)
    print("Testing various commands you can trigger with 'go' detection...")

    # Safe commands (won't open anything)
    test_command("Text-to-speech", ["say", "Go command detected"], safe=True)
    test_command("Get current date", ["date"], safe=True)
    test_command("List Applications", ["ls", "/Applications"], safe=True)

    print("\n" + "=" * 40)
    print("Interactive commands (will ask permission):")

    # Commands that open things (ask first)
    test_command("Open Chrome browser", ["open", "-a", "Google Chrome"], safe=False)
    test_command("Open Finder", ["open", "-a", "Finder"], safe=False)
    test_command("Open Calculator", ["open", "-a", "Calculator"], safe=False)
    test_command("Open default browser to Google", ["open", "https://google.com"], safe=False)
    test_command("Open Applications folder", ["open", "/Applications"], safe=False)

    print("\n" + "=" * 40)
    print("Other useful commands you can use:")
    print("• ['open', '-a', 'Spotify'] - Open Spotify")
    print("• ['open', '-a', 'Terminal'] - Open Terminal")
    print("• ['open', '-a', 'Visual Studio Code'] - Open VS Code")
    print("• ['osascript', '-e', 'tell application \"System Events\" to keystroke \"v\" using command down'] - Paste")
    print("• ['pmset', 'sleepnow'] - Put Mac to sleep")
    print("• ['say', 'Hello there'] - Text to speech")
    print("• ['open', 'https://youtube.com'] - Open YouTube")

if __name__ == "__main__":
    main()
