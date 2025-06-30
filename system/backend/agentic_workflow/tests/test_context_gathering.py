import json
from fastapi.testclient import TestClient
from system.backend.agentic_workflow.main import app
import os
import shutil

client = TestClient(app)

def test_run_stage_2():
    session_id = "test_session_123"
    artifacts_dir = f"artifacts/{session_id}"

    # Clean up before test
    if os.path.exists(artifacts_dir):
        shutil.rmtree(artifacts_dir)

    request_payload = {
        "session_id": session_id,
        "user_selected_screens": ["home", "about", "contact"],
        "stage_1_output": {
            "domain": "Portfolio Website",
            "industry_patterns": "Creative",
            "suggested_screens": ["home", "about", "contact", "portfolio"],
            "global_theme_hints": ["minimalist", "modern"]
        }
    }

    response = client.post("/context-gathering/stage-2", json=request_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["selected_screens"] == ["home", "about", "contact"]
    assert "home" in data["screen_requirements"]
    assert "about" in data["screen_requirements"]
    assert "contact" in data["screen_requirements"]
    assert "purpose" in data["screen_requirements"]["home"]

    # Check if the file was created
    output_file = f"artifacts/{session_id}/context/stage_2_screen_requirements.json"
    assert os.path.exists(output_file)

    # Verify file content
    with open(output_file, "r") as f:
        file_content = json.load(f)
    assert file_content["selected_screens"] == ["home", "about", "contact"]

    # Clean up after test
    shutil.rmtree(artifacts_dir) 