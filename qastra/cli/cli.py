import os
import subprocess

import click
from qastra.core.runner import run_tests, run_tests_parallel


@click.group()
def cli():
    """Qastra command-line interface."""
    pass


@cli.command()
@click.argument("path")
@click.option("--parallel", default=1, help="Number of parallel workers (default: 1)")
def run(path, parallel):
    """Run a single file or all .py files in a folder.
    
    Examples:
        qastra run tests                    # Sequential execution
        qastra run tests --parallel 4       # Parallel execution with 4 workers
        qastra run examples/demo_test.py    # Single file
    """
    if os.path.isfile(path):
        # Run single file
        print(f"[Qastra] Running single file: {path}")
        env = {**os.environ, "PYTHONPATH": "/Users/apple/Desktop/All Data/Qastra"}
        result = subprocess.run(["python3", path], capture_output=True, text=True, env=env)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    else:
        # Run folder with parallel or sequential execution
        if parallel > 1:
            run_tests_parallel(path, workers=parallel)
        else:
            run_tests(path)


@cli.command()
@click.argument("folder")
@click.option("--workers", default=4, help="Number of parallel workers (default: 4)")
def parallel(folder, workers):
    """Run tests in parallel mode.
    
    Example:
        qastra parallel tests --workers 8
    """
    run_tests_parallel(folder, workers=workers)


@cli.command()
@click.argument("url")
@click.option("--duration", default=60, help="Recording duration in seconds (default: 60)")
@click.option("--output", default="recorded_test.py", help="Output test file name (default: recorded_test.py)")
def record(url, duration, output):
    """Record browser interactions and generate automated tests.
    
    Examples:
        qastra record https://example.com
        qastra record https://example.com --duration 120
        qastra record https://example.com --output my_test.py
    """
    from qastra.recorder.recorder import start_recorder
    
    print("🎬 Starting Qastra Recorder...")
    print(f"🌐 URL: {url}")
    print(f"⏱️  Duration: {duration}s")
    print(f"📝 Output: {output}")
    
    start_recorder(url, duration=duration, output_file=output)


@cli.command()
@click.argument("folder")
def sequential(folder):
    """Run tests in sequential mode.
    
    Example:
        qastra sequential tests
    """
    run_tests(folder)

