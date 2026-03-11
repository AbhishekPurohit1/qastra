import os
import subprocess


def run_tests(folder):
    """Run all Python test files in a folder sequentially.
    
    Args:
        folder (str): Path to the folder containing test files
    """
    print(f"\n[VibeTest] Running tests from: {folder}")
    print("=" * 60)
    
    test_files = []
    for file in os.listdir(folder):
        if file.endswith(".py") and not file.startswith("__"):
            test_files.append(file)
    
    if not test_files:
        print("[VibeTest] No test files found!")
        return
    
    for test_file in test_files:
        print(f"\n[VibeTest] Executing: {test_file}")
        print("-" * 40)
        
        result = subprocess.run(
            ["python3", f"{folder}/{test_file}"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "/Users/apple/Desktop/All Data/VibeTest"}
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file} - PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {test_file} - FAILED")
            if result.stderr:
                print(result.stderr)
        
        print("-" * 40)


def test(name):
    """Simple DSL entry to label a test.
    
    Args:
        name (str): Test name/description
    """
    print(f"[VibeTest] Test: {name}")

