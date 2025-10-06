#!/usr/bin/env python3
"""Script to update version in all project files."""

import re
import sys
from pathlib import Path


def update_version(new_version: str) -> None:
    """Update version in all project files."""
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+(-\w+)?$', new_version):
        print(f"Error: Invalid version format '{new_version}'")
        print("Expected format: X.Y.Z or X.Y.Z-suffix (e.g., 1.0.0 or 1.0.0-beta)")
        sys.exit(1)
    
    project_root = Path(__file__).parent.parent
    files_updated = []
    
    # Update __version__.py
    version_file = project_root / "src" / "mongodb_query_builder" / "__version__.py"
    if version_file.exists():
        content = version_file.read_text()
        new_content = re.sub(
            r'__version__\s*=\s*["\']([^"\']+)["\']',
            f'__version__ = "{new_version}"',
            content
        )
        if new_content != content:
            version_file.write_text(new_content)
            files_updated.append(str(version_file.relative_to(project_root)))
    
    # Update pyproject.toml
    pyproject_file = project_root / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        new_content = re.sub(
            r'^version\s*=\s*["\']([^"\']+)["\']',
            f'version = "{new_version}"',
            content,
            flags=re.MULTILINE
        )
        if new_content != content:
            pyproject_file.write_text(new_content)
            files_updated.append("pyproject.toml")
    
    # Update setup.py if it exists and uses version
    setup_file = project_root / "setup.py"
    if setup_file.exists():
        content = setup_file.read_text()
        # Check if setup.py has a hardcoded version
        if re.search(r'version\s*=\s*["\'][^"\']+["\']', content):
            new_content = re.sub(
                r'version\s*=\s*["\']([^"\']+)["\']',
                f'version="{new_version}"',
                content
            )
            if new_content != content:
                setup_file.write_text(new_content)
                files_updated.append("setup.py")
    
    # Update mkdocs.yml if it has version info
    mkdocs_file = project_root / "mkdocs.yml"
    if mkdocs_file.exists():
        content = mkdocs_file.read_text()
        # Update version in extra section if present
        if 'version:' in content:
            new_content = re.sub(
                r'(extra:\s*\n(?:.*\n)*?\s*version:\s*\n\s*provider:\s*\w+\s*\n\s*default:\s*)(\w+)',
                f'\\g<1>{new_version}',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            if new_content != content:
                mkdocs_file.write_text(new_content)
                files_updated.append("mkdocs.yml")
    
    # Summary
    if files_updated:
        print(f"✅ Version updated to {new_version} in:")
        for file in files_updated:
            print(f"   - {file}")
    else:
        print(f"ℹ️  No files needed updating (already at version {new_version})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        print("Example: python update_version.py 1.0.2")
        sys.exit(1)
    
    update_version(sys.argv[1])
