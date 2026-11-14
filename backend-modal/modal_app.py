# pyright: reportMissingImports=false
from pathlib import Path
import modal

# 1. Cloud Container Setup (Lightweight packages + Backend Code)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .uv_pip_install(
        "fastapi[standard]",
        "python-dotenv",
        "groq",
        "pypdf",
        "python-docx",
        "ddgs",
        "python-multipart",
    )
    .add_local_dir(
        Path(__file__).parent,
        remote_path="/root",
        ignore=["storage_data", "__pycache__", ".venv", ".git"],
    )
)

app = modal.App("velo-ai-engine", image=image)

# 2. 24-Hour Persistent Storage Volume on Modal Cloud
velo_volume = modal.Volume.from_name("velo-ai-storage", create_if_missing=True)


# 3. Auto-load API Keys directly from your local .env file into Modal Cloud!
@app.function(
    secrets=[modal.Secret.from_dotenv(path=Path(__file__).parent)],
    volumes={"/data": velo_volume},
    timeout=300,
)
@modal.asgi_app()
def serve_cloud():
    import os
    os.environ["VELO_STORAGE_DIR"] = "/data/sessions"
    from main import app as fastapi_app
    return fastapi_app