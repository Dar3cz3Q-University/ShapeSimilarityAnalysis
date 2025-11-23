import os

OUTPUTS_DIR="outputs"
GENERATE_DIR=f"{OUTPUTS_DIR}/generate"
ANALYZE_DIR=f"{OUTPUTS_DIR}/analyze"

os.makedirs(GENERATE_DIR, exist_ok=True)
os.makedirs(ANALYZE_DIR, exist_ok=True)
