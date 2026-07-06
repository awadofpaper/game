# Quick script to run remaining systems test with minimal fixes
import subprocess
import sys

# Run the test and capture output
result = subprocess.run([sys.executable, "remaining_systems_stress_test.py"], 
                       capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
