import os


def write_code_files(file_data_list, base_dir="."):
    """
    Writes each code snippet to its respective file path under the given base directory.

    Args:
        file_data_list (list): List of dicts with 'file_path' and 'code_snippet'.
        base_dir (str): Base directory to write files into.
    """
    for item in file_data_list:
        file_path = os.path.join(base_dir, item["file_path"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(item["code_snippet"])
