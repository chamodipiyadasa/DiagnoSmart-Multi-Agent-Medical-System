"""Application configuration for the DiagnoSmart multi-agent system."""

from pathlib import Path

# Local Ollama model name. Example alternatives: phi3, qwen2.5:7b, mistral.
OLLAMA_MODEL: str = "llama3:8b"
OLLAMA_TEMPERATURE: float = 0.1
OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"

BASE_DIR: Path = Path(__file__).resolve().parent
DATA_PATH: Path = BASE_DIR / "data" / "diseases.json"
LOG_PATH: Path = BASE_DIR / "diagnosmart.log"

# Safety disclaimer required in final output.
MEDICAL_DISCLAIMER: str = "This is not a medical diagnosis. Please consult a doctor."
