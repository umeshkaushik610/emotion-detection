"""
Upload emotion classifier model to Hugging Face Hub
Run from project root: python upload_to_hf.py
"""
from lib2to3.pgen2 import token
from huggingface_hub import HfApi, create_repo, login
import os

# ═══════════════════════════════════════════════════
# UPDATE THESE VALUES
# ═══════════════════════════════════════════════════
HF_USERNAME = "umeshkaushik610"  # <-- Change this
REPO_NAME = "emotion-classifier"
# ═══════════════════════════════════════════════════

REPO_ID = f"{HF_USERNAME}/{REPO_NAME}"

# login with token directly
#login(token="my token ID")

print(f"Uploading model to: {REPO_ID}")
print("=" * 50)

# Create repo (public = free)
print("Creating/verifying repo...")
create_repo(REPO_ID, repo_type="model", exist_ok=True)

api = HfApi()

files_to_upload = [
    ("data/models/emotion_classifier_final.pt", "emotion_classifier_final.pt"),
    ("data/models/model_info.json", "model_info.json"),
    ("data/models/tokenizer/tokenizer.json", "tokenizer.json"),
    ("data/models/tokenizer/tokenizer_config.json", "tokenizer_config.json"),
]

for local_path, repo_path in files_to_upload:
    if os.path.exists(local_path):
        print(f"Uploading {local_path} -> {repo_path}...")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=repo_path,
            repo_id=REPO_ID
        )
        print(f"  Done!")
    else:
        print(f"  WARNING: {local_path} not found, skipping!")

print("=" * 50)
print(f"Upload complete! Visit: https://huggingface.co/{REPO_ID}")
print(f"\nNow update HF_REPO_ID in your inference.py and Streamlit secrets to: {REPO_ID}")
