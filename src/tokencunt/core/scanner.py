"""Repository scanner module for token estimation."""

import os
import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tokencunt.core.token_counter import TokenCounter


# Default patterns to ignore
DEFAULT_IGNORE_PATTERNS = [
    "node_modules/",
    ".git/",
    "__pycache__/",
    "*.pyc",
    ".venv/",
    "venv/",
    "env/",
    "dist/",
    "build/",
    "*.egg-info/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".tox/",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
]

# File extensions to scan
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
}
TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".env",
    ".sql",
    ".sh",
    ".bash",
}


@dataclass
class FileResult:
    """Result for a single file."""

    path: Path
    tokens: int
    lines: int


@dataclass
class ScanResult:
    """Result for a complete scan."""

    files: list[FileResult]
    total_tokens: int
    total_lines: int
    total_files: int
    scanned_files: int
    ignored_files: int

    def estimate_cost(
        self, input_cost_per_1k: float = 0.001, output_cost_per_1k: float = 0.003
    ) -> float:
        """Estimate cost for total tokens."""
        return (self.total_tokens / 1000) * input_cost_per_1k


class RepoScanner:
    """Scanner for estimating tokens in a repository."""

    def __init__(self, model: str = "gpt-4"):
        """Initialize scanner."""
        self.token_counter = TokenCounter(model=model)
        self.ignore_patterns = list(DEFAULT_IGNORE_PATTERNS)
        self.file_extensions = CODE_EXTENSIONS | TEXT_EXTENSIONS

    def load_ignore_file(self, path: Path) -> None:
        """
        Load ignore patterns from .tokencuntignore file.

        Args:
            path: Path to .tokencuntignore file
        """
        if not path.exists():
            return

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    self.ignore_patterns.append(line)

    def should_ignore(self, file_path: Path, root_path: Path) -> bool:
        """
        Check if a file should be ignored.

        Args:
            file_path: Full path to the file
            root_path: Root directory being scanned

        Returns:
            True if file should be ignored
        """
        # Get relative path for pattern matching
        try:
            rel_path = file_path.relative_to(root_path)
        except ValueError:
            return True

        # Convert to string for pattern matching
        rel_str = str(rel_path)
        path_parts = rel_path.parts

        for pattern in self.ignore_patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith("/"):
                dir_pattern = pattern.rstrip("/")
                for part in path_parts:
                    if fnmatch.fnmatch(part, dir_pattern):
                        return True
            # Handle file patterns
            else:
                if fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(
                    file_path.name, pattern
                ):
                    return True

        return False

    def is_supported(self, file_path: Path) -> bool:
        """Check if file extension is supported."""
        return file_path.suffix.lower() in self.file_extensions

    def count_file_tokens(self, file_path: Path) -> tuple[int, int]:
        """
        Count tokens in a single file.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (token_count, line_count)
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = len(content.splitlines())
                tokens = self.token_counter.estimate(content)
                return tokens, lines
        except (IOError, OSError):
            return 0, 0

    def scan_directory(
        self,
        path: Path,
        patterns: Optional[list[str]] = None,
        ignore_file: Optional[Path] = None,
    ) -> ScanResult:
        """
        Scan a directory recursively for token estimation.

        Args:
            path: Directory to scan
            patterns: Additional file patterns to match
            ignore_file: Path to .tokencuntignore file

        Returns:
            ScanResult with all file counts and totals
        """
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        # Load ignore file if provided
        if ignore_file:
            self.load_ignore_file(ignore_file)
        else:
            # Check for .tokencuntignore in the scan directory
            default_ignore = path / ".tokencuntignore"
            if default_ignore.exists():
                self.load_ignore_file(default_ignore)

        # Collect files
        files_to_scan: list[Path] = []
        ignored_count = 0

        for root, dirs, filenames in os.walk(path):
            root_path = Path(root)

            # Filter out ignored directories in-place
            dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d, path)]

            for filename in filenames:
                file_path = root_path / filename

                if self.should_ignore(file_path, path):
                    ignored_count += 1
                    continue

                if not self.is_supported(file_path):
                    continue

                files_to_scan.append(file_path)

        # Count tokens for each file
        results: list[FileResult] = []
        total_tokens = 0
        total_lines = 0

        for file_path in files_to_scan:
            tokens, lines = self.count_file_tokens(file_path)
            results.append(FileResult(path=file_path, tokens=tokens, lines=lines))
            total_tokens += tokens
            total_lines += lines

        return ScanResult(
            files=results,
            total_tokens=total_tokens,
            total_lines=total_lines,
            total_files=len(results),
            scanned_files=len(results),
            ignored_files=ignored_count,
        )
