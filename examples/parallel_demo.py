"""Parallel Execution Demo - Show performance improvements."""

from qastra import *
import time

qastra("Parallel Performance Demo")

print("🚀 Qastra Parallel Execution Demo")
print("=" * 50)

# Create multiple test scenarios to demonstrate parallel benefits
test_scenarios = [
    {"name": "Quick Test", "duration": 1},
    {"name": "Medium Test", "duration": 2},
    {"name": "Slow Test", "duration": 3},
    {"name": "Very Slow Test", "duration": 4}
]

print("\n📊 Test Scenarios:")
for scenario in test_scenarios:
    print(f"   • {scenario['name']} - {scenario['duration']}s")

print("\n⏱️  Sequential Execution Estimate:")
sequential_time = sum(s["duration"] for s in test_scenarios)
print(f"   Total time: {sequential_time}s")

print("\n🔥 Parallel Execution Estimate:")
# With 4 workers, the slowest test determines total time
parallel_time = max(s["duration"] for s in test_scenarios)
print(f"   Total time: {parallel_time}s (with 4 workers)")

print(f"\n⚡ Performance Improvement:")
improvement = ((sequential_time - parallel_time) / sequential_time) * 100
print(f"   {improvement:.0f}% faster!")
print(f"   {sequential_time - parallel_time}s saved!")

print("\n🎯 Real-World Benefits:")
print("   • 100 tests @ 30s each = 50 minutes sequential")
print("   • 100 tests @ 30s each (8 workers) = ~7 minutes parallel")
print("   • 7x faster execution!")

print("\n📋 CLI Commands:")
print("   qastra run tests                    # Sequential")
print("   qastra run tests --parallel 4       # Parallel (4 workers)")
print("   qastra run tests --parallel 8       # Parallel (8 workers)")
print("   qastra parallel tests --workers 6  # Explicit parallel command")

print("\n🌟 Parallel Execution Features:")
print("   ✅ Multiprocessing with process pools")
print("   ✅ Independent browser instances per test")
print("   ✅ Timeout protection (5 minutes per test)")
print("   ✅ Detailed result reporting")
print("   ✅ Performance metrics and time savings")
print("   ✅ Error handling and crash protection")

print("\n🚀 Production Ready!")
print("   Qastra parallel execution scales to hundreds of tests!")
