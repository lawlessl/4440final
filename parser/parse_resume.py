import subprocess
import json
import csv
import os

# Input PDF file
pdf_path = "/Users/liamlawless/Documents/Job Stuff/DS4440.pdf"

# Output CSV path
output_dir = "/Users/liamlawless/Desktop/Northeastern/2024-2025 School Year/DS4440/4440final/temp/parsed_resumes"
#output_file = os.path.join(output_dir, "DS4440_parsed.csv")

# Command to run the TypeScript parser
command = ["npx", "ts-node", "parser/lib/run.ts", pdf_path]

try:
    # Run the TS script
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    parsed_resume = json.loads(result.stdout)

except subprocess.CalledProcessError as e:
    print("Error while running TS parser:\n", e.stderr)
except json.JSONDecodeError as e:
    print("Error parsing JSON output:\n", result.stdout)
except Exception as e:
    print("Unexpected error:\n", str(e))
