import os
import subprocess
from multiprocessing import Pool
import time
from qastra.reporter.reporter import generate_report


def run_single_test(test_file_path, debug=False):
    """Run a single test file with proper environment.
    
    Args:
        test_file_path (str): Full path to the test file
        debug (bool): Enable debug mode with detailed logging
        
    Returns:
        dict: Test result with file path, status, output, and execution time
    """
    start_time = time.time()
    file_name = os.path.basename(test_file_path)
    
    # Set up environment for this test
    env = {**os.environ, "PYTHONPATH": "/Users/apple/Desktop/All Data/Qastra"}
    
    if debug:
        print(f"[DEBUG] Running test: {file_name}")
        print(f"[DEBUG] Path: {test_file_path}")
        print(f"[DEBUG] Environment: PYTHONPATH={env['PYTHONPATH']}")
        print()
    
    try:
        result = subprocess.run(
            ["python3", test_file_path],
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout per test
        )
        
        execution_time = time.time() - start_time
        
        if debug:
            print(f"[DEBUG] Test completed in {execution_time:.2f}s")
            print(f"[DEBUG] Return code: {result.returncode}")
            if result.stdout:
                print(f"[DEBUG] STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"[DEBUG] STDERR:\n{result.stderr}")
            print()
        
        return {
            "file": file_name,
            "path": test_file_path,
            "status": "passed" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "execution_time": execution_time,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        if debug:
            print(f"[DEBUG] Test timed out after 5 minutes")
        
        return {
            "file": file_name,
            "path": test_file_path,
            "status": "timeout",
            "output": "",
            "error": "Test timed out after 5 minutes",
            "execution_time": time.time() - start_time,
            "returncode": -1
        }
    except Exception as e:
        return {
            "file": file_name,
            "path": test_file_path,
            "status": "error",
            "output": "",
            "error": str(e),
            "execution_time": time.time() - start_time
        }


def run_tests_parallel(test_dir, workers=4, debug=False):
    """Run all Python test files in a directory using multiprocessing.
    
    Args:
        test_dir (str): Directory containing test files
        workers (int): Number of parallel workers
        debug (bool): Enable debug mode with detailed logging
    """
    if not os.path.exists(test_dir):
        print(f"❌ Directory not found: {test_dir}")
        return []
    
    # Find all Python test files
    test_files = []
    for file in os.listdir(test_dir):
        if file.endswith('.py') and not file.startswith('__'):
            test_files.append(os.path.join(test_dir, file))
    
    if not test_files:
        print(f"❌ No test files found in: {test_dir}")
        return []
    
    print(f"🚀 Running {len(test_files)} test(s) in parallel with {workers} workers...")
    if debug:
        print(f"[DEBUG] Test files found: {test_files}")
        print(f"[DEBUG] Using {workers} parallel workers")
        print()
    
    # Create wrapper function that includes debug flag
    def run_with_debug(test_file):
        return run_single_test(test_file, debug=debug)
    
    # Run tests in parallel
    with Pool(workers) as pool:
        results = pool.map(run_with_debug, test_files)
    
    # Sort results by execution time for display
    results.sort(key=lambda x: x['execution_time'])
    
    # Print results
    for result in results:
        status_icon = "✅" if result["status"] == "passed" else "❌"
        print(f"{status_icon} {result['file']} ({result['execution_time']:.2f}s)")
        
        if result["status"] == "failed":
            print(f"   Error: {result['error'][:100]}...")
    
    # Summary
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = len(results) - passed
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    # Calculate performance metrics
    total_time = sum(r['execution_time'] for r in results)
    avg_time = total_time / len(results)
    print(f"⚠️ Could not generate HTML report: {e}")


def run_tests(folder):
    """Run all Python test files in a folder sequentially.
    
    Args:
        folder (str): Path to the folder containing test files
    """
    print(f"\n[Qastra] Running tests in SEQUENTIAL mode")
    print(f"📁 Folder: {folder}")
    print("=" * 60)
    
    test_files = []
    for file in os.listdir(folder):
        if file.endswith(".py") and not file.startswith("__"):
            test_files.append(file)
    
    if not test_files:
        print("[Qastra] No test files found!")
        return
    
    print(f"📋 Found {len(test_files)} test files")
    print(f"🐌 Starting sequential execution...")
    print("-" * 60)
    
    start_time = time.time()
    results = []
    
    for test_file in test_files:
        result = run_single_test(os.path.join(folder, test_file))
        results.append(result)
        
        status_icon = ""
        if result["status"] == "passed":
            status_icon = "✅"
        elif result["status"] == "failed":
            status_icon = "❌"
        elif result["status"] == "timeout":
            status_icon = "⏰"
        else:
            status_icon = "💥"
            
        print(f"{status_icon} {result['file']} ({result['execution_time']:.1f}s)")
        
        if result["output"]:
            print(f"   Output: {result['output'][:200]}...")
        if result["error"] and result["status"] == "failed":
            print(f"   Error: {result['error'][:100]}...")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Summary
    passed = len([r for r in results if r["status"] == "passed"])
    failed = len([r for r in results if r["status"] != "passed"])
    
    print("-" * 60)
    print(f"📈 SUMMARY:")
    print(f"   Total: {len(test_files)} tests")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏱️  Total time: {total_time:.1f}s")
    print(f"   🐌 Sequential execution")
    
    # Generate HTML report
    print("\n📊 Generating HTML report...")
    try:
        generate_report(results, start_time, end_time, auto_open=True)
    except Exception as e:
        print(f"⚠️ Could not generate HTML report: {e}")


def qastra(name):
    """Simple DSL entry to label a test.
    
    Args:
        name (str): Test name/description
    """
    print(f"[Qastra] Test: {name}")

