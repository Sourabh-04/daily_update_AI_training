"""Download the public Qwen model used by agent.py (run once after cloning).

Run: python download_model.py
No HF_TOKEN or API key required. Saves to ./Models/Qwen2.5-0.5B-Instruct
"""
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parent
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_DIR = ROOT / "Models" / "Qwen2.5-0.5B-Instruct"

print("Downloading public model:", MODEL_ID)
print("Saving inside project:", MODEL_DIR)

snapshot_download(
    repo_id=MODEL_ID,
    local_dir=str(MODEL_DIR),
    allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt"],
)

print("\nModel downloaded successfully! Next: python agent.py")
