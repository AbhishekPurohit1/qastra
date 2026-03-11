import os
import subprocess

import click


@click.group()
def cli():
    """VibeTest command-line interface."""
    pass


@cli.command()
@click.argument("path")
def run(path):
    """Run a single file or all .py files in a folder."""
    # Set PYTHONPATH to include the current directory
    env = {**os.environ, "PYTHONPATH": "/Users/apple/Desktop/All Data/VibeTest"}
    
    if os.path.isfile(path):
        result = subprocess.run(["python3", path], capture_output=True, text=True, env=env)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    else:
        for file in os.listdir(path):
            if file.endswith(".py") and not file.startswith("__"):
                print(f"\n[VibeTest] Running {file}")
                print("-" * 40)
                result = subprocess.run(["python3", f"{path}/{file}"], capture_output=True, text=True, env=env)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)

