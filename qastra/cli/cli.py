import os
import subprocess
import time

import click
from qastra.core.runner import run_tests, run_tests_parallel
from qastra.core.parser import parse_qa_file
from qastra.core.executor import execute_commands
from qastra.utils.logger import get_logger


@click.group()
def cli():
    """Qastra command-line interface."""


@cli.command()
@click.argument("path")
@click.option("--parallel", "parallel_workers", default=1, help="Number of parallel workers (default: 1)")
@click.option("--browser", default=None, help="Browser to use (chrome, firefox, safari, edge)")
@click.option("--headless", is_flag=True, help="Run in headless mode")
@click.option("--debug", is_flag=True, help="Enable debug mode with detailed logging")
def run(path, parallel_workers, browser, headless, debug):
    """Run tests from a `.qa` file or Python test files in a folder.

    Examples:
        qastra run tests                    # Sequential execution of .py tests
        qastra run tests --parallel 4       # Parallel execution with 4 workers
        qastra run tests --browser chrome      # Use Chrome browser
        qastra run tests --headless           # Run in headless mode
        qastra run tests --debug              # Enable debug mode
        qastra run examples/demo_test.py    # Single Python file
        qastra run login.qa                 # Qastra DSL test file
    """
    # Set debug mode globally
    if debug:
        os.environ["QASTRA_DEBUG"] = "1"
        print("🐛 Debug mode enabled")
        print("   - Parsed commands will be shown")
        print("   - Locator attempts will be displayed")
        print("   - Execution timing will be logged")
        print()
    
    # Set browser preference
    if browser:
        os.environ["QASTRA_BROWSER"] = browser.lower()
        print(f"🌐 Browser set to: {browser}")
    
    # Set headless mode
    if headless:
        os.environ["QASTRA_HEADLESS"] = "1"
        print("🔇 Headless mode enabled")
    
    if os.path.isfile(path):
        # `.qa` file → use Qastra DSL pipeline
        if path.endswith(".qa"):
            print(f"[Qastra] Running QA script: {path}")
            if debug:
                print(f"[DEBUG] Parsing .qa file: {path}")
            commands = parse_qa_file(path)
            if debug:
                print(f"[DEBUG] Parsed {len(commands)} commands:")
                for i, cmd in enumerate(commands):
                    print(f"   {i+1}. {cmd.action} -> {cmd.payload}")
                print()
            execute_commands(commands)
            return

        # Fallback: run single Python file directly
        print(f"[Qastra] Running single file: {path}")
        env = {**os.environ, "PYTHONPATH": "/Users/apple/Desktop/All Data/Qastra"}
        result = subprocess.run(["python3", path], capture_output=True, text=True, env=env)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    else:
        # Run folder with parallel or sequential execution for Python tests
        if parallel_workers > 1:
            print(f"[Qastra] Running tests in parallel with {parallel_workers} workers")
            run_tests_parallel(path, workers=parallel_workers, debug=debug)
        else:
            print("[Qastra] Running tests sequentially")
            run_tests(path, debug=debug)


@cli.command()
@click.argument("folder")
@click.option("--workers", default=4, help="Number of parallel workers (default: 4)")
@click.option("--debug", is_flag=True, help="Enable debug mode with detailed logging")
def parallel(folder, workers, debug):
    """Run tests in parallel mode.
    
    Example:
        qastra parallel tests --workers 8
        qastra parallel tests --debug
    """
    if debug:
        os.environ["QASTRA_DEBUG"] = "1"
        print("🐛 Debug mode enabled")
    
    print(f"[Qastra] Running tests in parallel with {workers} workers")
    run_tests_parallel(folder, workers=workers, debug=debug)


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

