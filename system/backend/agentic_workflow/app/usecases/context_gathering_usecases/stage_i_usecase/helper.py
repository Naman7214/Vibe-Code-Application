import json
import os
from typing import Any, Dict


def get_stage_file_path(session_id: str) -> str:
    """
    Generate the file path for stage_i.json based on session_id

    :param session_id: The session identifier
    :return: Full path to the stage_i.json file
    """
    return f"artifacts/{session_id}/project_context/stage_i.json"


def read_stage_data(file_path: str) -> Dict[str, Any]:
    """
    Read and parse stage_i.json data from file

    :param file_path: Path to the stage_i.json file
    :return: Parsed JSON data as dictionary
    :raises FileNotFoundError: If the file doesn't exist
    :raises json.JSONDecodeError: If the file contains invalid JSON
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Stage I file not found: {file_path}")

    with open(file_path, "r") as f:
        return json.load(f)


def update_screens_data(
    stage_data: Dict[str, Any],
    dict_of_screens: Dict[str, Any],
    is_follow_up: bool,
) -> Dict[str, Any]:
    """
    Update screens data based on follow-up flag

    :param stage_data: Current stage data
    :param dict_of_screens: New screens data to add/replace
    :param is_follow_up: Whether this is a follow-up request
    :return: Updated stage data
    """
    if not is_follow_up:
        # Replace screens field with dict_of_screens
        stage_data["screens"] = dict_of_screens
    else:
        # Append dict_of_screens to existing screens field
        if "screens" not in stage_data:
            stage_data["screens"] = {}
        stage_data["screens"].update(dict_of_screens)

    return stage_data


def write_stage_data(file_path: str, stage_data: Dict[str, Any]) -> None:
    """
    Write stage data to JSON file

    :param file_path: Path where to write the JSON file
    :param stage_data: Data to write to the file
    :raises IOError: If there's an error writing to the file
    """
    with open(file_path, "w") as f:
        json.dump(stage_data, f, indent=2)
