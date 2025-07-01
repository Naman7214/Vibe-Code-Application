import os
from pathlib import Path


def generate_directory_structure(
    directory_path: str,
    prefix: str = "",
    max_depth: int = 5,
    current_depth: int = 0,
) -> str:
    """
    Generate directory structure as a string with absolute path at root

    Args:
        directory_path: Path to the directory to analyze
        prefix: Prefix for tree structure display
        max_depth: Maximum depth to traverse
        current_depth: Current depth level

    Returns:
        String representation of directory structure with absolute root path
    """
    if current_depth >= max_depth or not os.path.exists(directory_path):
        return ""

    # For the root level, show the absolute path
    if current_depth == 0:
        structure = f"{directory_path}/\n"
    else:
        structure = ""

    try:
        items = sorted(os.listdir(directory_path))
        for i, item in enumerate(items):
            if item.startswith("."):
                continue

            item_path = os.path.join(directory_path, item)
            is_last = i == len(items) - 1

            current_prefix = "└── " if is_last else "├── "
            structure += f"{prefix}{current_prefix}{item}\n"

            if os.path.isdir(item_path) and not item.startswith("."):
                next_prefix = prefix + ("    " if is_last else "│   ")
                structure += generate_directory_structure(
                    item_path, next_prefix, max_depth, current_depth + 1
                )
    except PermissionError:
        pass

    return structure


def get_project_root():
    current = Path(__file__).resolve()

    # Look for velocity.new specific markers
    markers = ["requirements.txt", "system", "artifacts"]

    for parent in current.parents:
        if all((parent / marker).exists() for marker in markers):
            return str(parent)

    return str(current.parent)
