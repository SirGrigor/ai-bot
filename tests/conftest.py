import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variables for testing
os.environ["TELEGRAM_TOKEN"] = "test_token"
os.environ["ANTHROPIC_API_KEY"] = "test_key"
