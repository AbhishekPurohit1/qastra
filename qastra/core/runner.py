import os
import subprocess
from multiprocessing import Pool
import time
from qastra.reporter.reporter import generate_report


def run_single_test(test_file_path):
    """Run a single test file with proper environment.
    
    Args:
        test_file_path (str): Full path to the test file
        
    Returns:
        dict: Test result with file path, status, output, and execution time
    """
    start_time = time.time()
    file_name = os.path.basename(test_file_path)
    
    # Set up environment for this test
    env = {**os.environ, "PYTHONPATH": "/Users/apple/Desktop/All Data/Qastra"}
    
    try:
        result = subprocess.run(
            ["python3", test_file_path],
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout per test
        )
        
        execution_time = time.time() - start_time
        
        return {
            "file": file_name,
            "path": test_file_path,
            "status": "passed" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "execution_time": execution_time
        }
        
    except subprocess.TimeoutExpired:
        return {
            "file": file_name,
            "path": test_file_path,
            "status": "timeout",
            "output": "",
            "error": "Test timed out after 5 minutes",
            "execution_time": time.time() - start_time
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


def run_tests_parallel(folder, workers=4):
    """Run all Python test files in a folder using multiple workers.
    
    Args:
        folder (str): Path to the folder containing test files
        workers (int): Number of parallel workers
    """
    print(f"\n[Qastra] Running tests in PARALLEL mode")
    print(f"📁 Folder: {folder}")
    print(f"🔧 Workers: {workers}")
    print("=" * 60)
    
    # Find all test files
    test_files = []
    for file in os.listdir(folder):
        if file.endswith(".py") and not file.startswith("__"):
            test_files.append(os.path.join(folder, file))
    
    if not test_files:
        print("[Qastra] No test files found!")
        return
    
    print(f"📋 Found {len(test_files)} test files")
    print(f"🚀 Starting parallel execution...")
    print("-" * 60)
    
    # Run tests in parallel
    start_time = time.time()
    
    with Pool(workers) as pool:
        results = pool.map(run_single_test, test_files)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Process and display results
    passed = 0
    failed = 0
    timeouts = 0
    errors = 0
    
    print("\n📊 PARALLEL TEST RESULTS:")
    print("=" * 60)
    
    for result in results:
        status_icon = ""
        if result["status"] == "passed":
            status_icon = "✅"
            passed += 1
        elif result["status"] == "failed":
            status_icon = "❌"
            failed += 1
        elif result["status"] == "timeout":
            status_icon = "⏰"
            timeouts += 1
        else:
            status_icon = "💥"
            errors += 1
            
        print(f"{status_icon} {result['file']} ({result['execution_time']:.1f}s)")
        
        if result["status"] == "failed" and result["error"]:
            print(f"   Error: {result['error'][:100]}...")
        elif result["status"] == "timeout":
            print(f"   ⚠️ Test timed out")
        elif result["status"] == "error":
            print(f"   💥 {result['error']}")
    
    # Summary
    print("-" * 60)
    print(f"📈 SUMMARY:")
    print(f"   Total: {len(results)} tests")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏰ Timeouts: {timeouts}")
    print(f"   💥 Errors: {errors}")
    print(f"   ⏱️  Total time: {total_time:.1f}s")
    print(f"   🔥 Workers: {workers}")
    
    if workers > 1:
        estimated_sequential_time = sum(r["execution_time"] for r in results)
        time_saved = estimated_sequential_time - total_time
        print(f"   ⚡ Time saved: ~{time_saved:.1f}s ({(time_saved/estimated_sequential_time*100):.0f}% faster)")
    
    # Generate HTML report
    print("\n📊 Generating HTML report...")
    try:
        generate_report(results, start_time, end_time, auto_open=True)
    except Exception as e:
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

