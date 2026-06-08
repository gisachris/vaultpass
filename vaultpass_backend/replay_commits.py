#!/usr/bin/env python3

import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, env=None):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


def file_exists(path):
    return Path(path).exists()


def main():
    json_file = "commits.json"

    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        sys.exit(1)

    with open(json_file, "r", encoding="utf-8") as f:
        commits = json.load(f)

    for commit in commits:
        date = commit["date"]
        message = commit["message"]
        files = commit["files"]

        existing_files = [f for f in files if file_exists(f)]

        if not existing_files:
            print(f"Skipping commit '{message}' - no files found")
            continue

        # Stage only the files for this commit
        run(["git", "add", "--"] + existing_files)

        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date

        try:
            run(
                ["git", "commit", "-m", message],
                env=env,
            )
        except subprocess.CalledProcessError:
            print(f"No changes for commit: {message}")

    print("Done.")


if __name__ == "__main__":
    main()