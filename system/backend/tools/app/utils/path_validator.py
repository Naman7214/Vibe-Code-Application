import os
from typing import List, Tuple

# Define system directories that are off-limits (only critical system paths)
SYSTEM_DIRECTORIES = [
    os.path.abspath("system"),
    os.path.abspath("system/backend"),
    os.path.abspath("system/orchestrator_workflow"),
    os.path.abspath("system/mcp_server"),
    os.path.abspath("system/custom_orchestrator_workflow"),
    os.path.abspath("system/frontend"),
]

# Define any additional paths that should be protected (system paths only)
PROTECTED_ROOT_PATHS = [
    "/bin",
    "/sbin",
    "/usr",
    "/etc",
    "/var",
    "/system",
    "/library",
    # Add any other system paths that should be protected
]


def get_common_exclusion_patterns() -> List[str]:
    """
    Returns a list of common directories and files that should be excluded
    from search operations, file listings, and other file operations.

    Returns:
        List of glob patterns to exclude
    """
    return [
        # Python virtual environments
        ".venv",
        "venv",
        ".env",
        "env",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        # Node.js/JavaScript
        "node_modules",
        "package-lock.json",
        "yarn.lock",
        "npm-debug.log*",
        "yarn-debug.log*",
        "yarn-error.log*",
        ".npm",
        ".yarn",
        # React/Next.js
        ".next",
        "dist",
        "build",
        ".nuxt",
        ".output",
        ".cache",
        # Flutter/Dart
        ".dart_tool",
        ".flutter-plugins",
        ".flutter-plugins-dependencies",
        ".packages",
        "pubspec.lock",
        ".fvm",
        ".idea",
        ".vscode",
        "android",
        "ios",
        "windows",
        "macos",
        "linux",
        "web",
        "build",
        ".flutter",
        ".metadata",
        "*.g.dart",
        "*.freezed.dart",
        "*.mocks.dart",
        "*.config.dart",
        # Version control
        ".git",
        ".gitignore",
        ".gitmodules",
        ".svn",
        ".hg",
        # IDEs and editors
        ".idea",
        ".vscode",
        ".vs",
        "*.swp",
        "*.swo",
        "*~",
        # OS specific
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        # Build artifacts
        "*.log",
        "coverage",
        ".nyc_output",
        "*.tmp",
        "*.temp",
    ]


def get_directory_exclusion_patterns() -> List[str]:
    """
    Returns directory names that should be excluded from directory listings
    and recursive operations.

    Returns:
        List of directory names to exclude
    """
    return [
        # Python virtual environments
        ".venv",
        "venv",
        ".env",
        "env",
        "__pycache__",
        # Node.js/JavaScript
        "node_modules",
        ".npm",
        ".yarn",
        # React/Next.js
        ".next",
        "dist",
        "build",
        ".nuxt",
        ".output",
        ".cache",
        # Flutter/Dart
        ".dart_tool",
        ".fvm",
        ".idea",
        ".vscode",
        "android",
        "ios",
        "windows",
        "macos",
        "linux",
        "web",
        "build",
        ".flutter",
        # Version control
        ".git",
        ".svn",
        ".hg",
        # IDEs and editors
        ".idea",
        ".vscode",
        ".vs",
        # OS specific
        ".DS_Store",
        # Build artifacts
        "coverage",
        ".nyc_output",
    ]


def get_ripgrep_exclusion_patterns() -> List[str]:
    """
    Returns exclusion patterns specifically formatted for ripgrep (-g flag).

    Returns:
        List of patterns to exclude for ripgrep
    """
    return [
        # Python virtual environments
        "!.venv/",
        "!venv/",
        "!.env/",
        "!env/",
        "!__pycache__/",
        "!*.pyc",
        "!*.pyo",
        "!*.pyd",
        # Node.js/JavaScript
        "!node_modules/",
        "!package-lock.json",
        "!yarn.lock",
        "!npm-debug.log*",
        "!yarn-debug.log*",
        "!yarn-error.log*",
        "!.npm/",
        "!.yarn/",
        # React/Next.js
        "!.next/",
        "!dist/",
        "!build/",
        "!.nuxt/",
        "!.output/",
        "!.cache/",
        # Flutter/Dart
        "!.dart_tool/",
        "!.flutter-plugins",
        "!.flutter-plugins-dependencies",
        "!.packages",
        "!pubspec.lock",
        "!.fvm/",
        "!.idea/",
        "!.vscode/",
        "!android/",
        "!ios/",
        "!windows/",
        "!macos/",
        "!linux/",
        "!web/",
        "!build/",
        "!.flutter/",
        "!.metadata",
        "!*.g.dart",
        "!*.freezed.dart",
        "!*.mocks.dart",
        "!*.config.dart",
        # Version control
        "!.git/",
        "!.gitignore",
        "!.gitmodules",
        "!.svn/",
        "!.hg/",
        # IDEs and editors
        "!.idea/",
        "!.vscode/",
        "!.vs/",
        "!*.swp",
        "!*.swo",
        "!*~",
        # OS specific
        "!.DS_Store",
        "!Thumbs.db",
        "!desktop.ini",
        # Build artifacts
        "!*.log",
        "!coverage/",
        "!.nyc_output/",
        "!*.tmp",
        "!*.temp",
    ]


def is_safe_path(path: str) -> Tuple[bool, str]:
    """
    Check if a path is safe to access (not in system directories or protected paths).

    Args:
        path: The path to check

    Returns:
        Tuple containing:
            - Boolean indicating if the path is safe
            - Error message if path is not safe, None otherwise
    """
    # Convert to absolute path for reliable checking
    abs_path = os.path.abspath(path)

    # Check if path is in a system directory
    for system_dir in SYSTEM_DIRECTORIES:
        if abs_path.startswith(system_dir):
            return False, f"Path '{path}' is in a protected system directory"

    # Check if path is in a protected root path
    for protected_path in PROTECTED_ROOT_PATHS:
        if abs_path.startswith(protected_path):
            return False, f"Path '{path}' is in a protected system path"

    # Allow access to project files including artifacts directory
    # Path is considered safe if no checks failed
    return True, ""
