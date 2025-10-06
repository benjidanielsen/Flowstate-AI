import os
import shutil
from typing import List

class FileManager:
    """Handles file operations such as reading, writing, merging files, and cleanup."""

    @staticmethod
    def read_file(file_path: str) -> str:
        """Read the content of a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """Write content to a file (overwrite if exists)."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def append_file(file_path: str, content: str) -> None:
        """Append content to a file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def merge_files(file_paths: List[str], output_file: str, separator: str = "\n") -> None:
        """Merge multiple files into one output file, separated by the given separator."""
        merged_content = []
        for path in file_paths:
            if os.path.exists(path) and os.path.isfile(path):
                content = FileManager.read_file(path)
                merged_content.append(content)
        FileManager.write_file(output_file, separator.join(merged_content))

    @staticmethod
    def delete_file(file_path: str) -> None:
        """Delete a file if it exists."""
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)

    @staticmethod
    def cleanup_dir(dir_path: str, remove_hidden: bool = False) -> None:
        """Delete all files and folders in the given directory.

        Args:
            dir_path: directory to clean up
            remove_hidden: if True, also remove hidden files and folders
        """
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return

        for entry in os.listdir(dir_path):
            if not remove_hidden and entry.startswith('.'):  # Skip hidden files/folders
                continue
            full_path = os.path.join(dir_path, entry)
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)

    @staticmethod
    def copy_file(src: str, dst: str) -> None:
        """Copy a file from src to dst."""
        if os.path.exists(src) and os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    @staticmethod
    def move_file(src: str, dst: str) -> None:
        """Move (rename) a file from src to dst."""
        if os.path.exists(src) and os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
