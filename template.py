import os


def create_dir_structure(base_path):
    directories = [
        "app/config",
        "app/controllers",
        "app/models/domain",
        "app/models/schemas",
        "app/repositories",
        "app/apis",
        "app/services",
        "app/utils",
    ]

    files = [
        "app/config/database.py",
        "app/config/settings.py",
        "app/utils/error_handler.py" "app/.env",
        "app/main.py",
        # ".gitignore",
        # "readme.md",
        # "track.md"
    ]

    # Create directories
    for directory in directories:
        os.makedirs(os.path.join(base_path, directory), exist_ok=True)

        # Create __init__.py in each directory
        init_path = os.path.join(base_path, directory, "__init__.py")
        with open(init_path, "w") as f:
            f.write("")

    # Create files
    for file in files:
        file_path = os.path.join(base_path, file)
        with open(file_path, "w") as f:
            f.write("# Placeholder for " + os.path.basename(file))


if __name__ == "__main__":
    create_dir_structure(
        "/Users/krishgoyani/Developer/velocity.new/system/backend/agentic_workflow"
    )
