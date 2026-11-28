import os
import sys
import tempfile
from pathlib import Path

# Settings are read at import time, so point everything at a temp folder first.
_tmp = Path(tempfile.mkdtemp(prefix="publisher-test-"))
os.environ["PUBLISHER_DATA_DIR"] = str(_tmp / "data")
os.environ["PIPELINE_OUTPUT_DIR"] = str(_tmp / "output")
os.environ["PUBLISHER_DRY_RUN"] = "1"
os.environ["APP_PASSWORD"] = ""
for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "META_APP_ID", "META_APP_SECRET",
          "TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"):
    os.environ[k] = "test"
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402


@pytest.fixture
def tmp_root():
    return _tmp
