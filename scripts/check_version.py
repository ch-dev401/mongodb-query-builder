#!/usr/bin/env python3
"""Script to check current version in project files."""

import re
from pathlib import Path


def check_versions():
    """Check and display versions from all project files."""
    project_root = Path(__file__).parent.parent
    
    print("Current version information:")
    
    # Check pyproject.toml
    pyproject_file = project_root / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        version = match.group(1) if match else "not found"
        print(f"  pyproject.toml: {version}")
    else:
        print(f"  pyproject.toml: file not found")
    
    # Check __version__.py
    version_file = project_root / "src" / "mongodb_query_builder" / "__version__.py"
    if version_file.exists():
        content = version_file.read_text()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        version = match.group(1) if match else "not found"
        print(f"  __version__.py: {version}")
    else:
        print(f"  __version__.py: file not found")
    
    # Check setup.py if it has version
    setup_file = project_root / "setup.py"
    if setup_file.exists():
        content = setup_file.read_text()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            version = match.group(1)
            print(f"  setup.py: {version}")


if __name__ == "__main__":
    check_versions()
