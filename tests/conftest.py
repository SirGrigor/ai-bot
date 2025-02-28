import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variables for testing
os.environ["TELEGRAM_TOKEN"] = "7805940448:AAHZAbaHV1ZDNs0FBqtdGczi3g_JYdgdrJE"
os.environ["ANTHROPIC_API_KEY"] = "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"
