"""Repository scanner for token estimation across entire projects."""

import fnmatch
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable

from tokencunt.core.token_counter import TokenCounter


# Default ignore patterns
DEFAULT_IGNORES = [
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "*.egg-info",
    ".tox",
    "vendor",
    "target",
]

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".txt",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".env",
    ".sh",
    ".bash",
    ".zsh",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
}


@dataclass
class FileResult:
    """Result for a single file scan."""

    path: Path
    tokens: int
    lines: int
    size_bytes: int


@dataclass
class ScanResult:
    """Result of a complete repository scan."""

    files: list[FileResult] = field(default_factory=list)
    total_tokens: int = 0
    total_lines: int = 0
    total_files: int = 0
    total_size_bytes: int = 0

    # Estimated cost (assuming $0.001 per 1K input tokens)
    estimated_cost: float = 0.0

    # File counts by extension
    files_by_extension: dict[str, int] = field(default_factory=dict)
    tokens_by_extension: dict[str, int] = field(default_factory=dict)

    def add_file(self, result: FileResult) -> None:
        """Add a file result to the scan."""
        self.files.append(result)
        self.total_tokens += result.tokens
        self.total_lines += result.lines
        self.total_size_bytes += result.size_bytes
        self.total_files += 1

        # Update extension stats
        ext = result.path.suffix.lower() or "no_ext"
        self.files_by_extension[ext] = self.files_by_extension.get(ext, 0) + 1
        self.tokens_by_extension[ext] = (
            self.tokens_by_extension.get(ext, 0) + result.tokens
        )

        # Estimate cost (rough estimate: $0.001 per 1K tokens)
        self.estimated_cost = (self.total_tokens / 1000) * 0.001


class RepoScanner:
    """Scanner for analyzing token counts across a repository."""

    def __init__(
        self,
        ignore_patterns: Optional[list[str]] = None,
        extensions: Optional[set[str]] = None,
    ):
        """
        Initialize the scanner.

        Args:
            ignore_patterns: List of patterns to ignore (fnmatch style)
            extensions: Set of file extensions to include (with dots)
        """
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORES.copy()
        self.extensions = extensions or SUPPORTED_EXTENSIONS
        self.token_counter = TokenCounter()
        self._loaded_ignores: list[str] = []

    def load_ignore_file(self, path: Path) -> None:
        """
        Load ignore patterns from a file.

        Args:
            path: Path to .tokencuntignore file
        """
        if not path.exists():
            return

        patterns = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                patterns.append(line)

        self._loaded_ignores = patterns

    def should_ignore(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored.

        Args:
            file_path: Path to check

        Returns:
            True if file should be ignored
        """
        path_str = str(file_path)
        relative_path = file_path.name

        # Check against default patterns and loaded ignores
        all_patterns = self.ignore_patterns + self._loaded_ignores

        for pattern in all_patterns:
            # Directory pattern (ends with /)
            if pattern.endswith("/"):
                dir_pattern = pattern.rstrip("/")
                if dir_pattern in path_str.split(os.sep):
                    return True
            # File/directory name pattern
            elif fnmatch.fnmatch(relative_path, pattern):
                return True
            # Path contains pattern
            elif pattern in path_str:
                return True

        return False

    def count_file_tokens(self, file_path: Path) -> Optional[FileResult]:
        """
        Count tokens in a single file.

        Args:
            file_path: Path to file

        Returns:
            FileResult with token count, or None if file should be skipped
        """
        if not file_path.exists():
            return None

        if self.should_ignore(file_path):
            return None

        # Check if extension is supported
        if file_path.suffix.lower() not in self.extensions:
            return None

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None

        tokens = self.token_counter.count(content)
        lines = len(content.splitlines())
        size = file_path.stat().st_size

        return FileResult(
            path=file_path,
            tokens=tokens,
            lines=lines,
            size_bytes=size,
        )

    def scan_directory(
        self,
        path: Path,
        patterns: Optional[list[str]] = None,
    ) -> ScanResult:
        """
        Scan a directory recursively for token estimation.

        Args:
            path: Root directory to scan
            patterns: Optional additional ignore patterns

        Returns:
            ScanResult with aggregated token counts
        """
        result = ScanResult()

        if patterns:
            self.ignore_patterns.extend(patterns)

        if not path.exists():
            return result

        if not path.is_dir():
            # Single file
            file_result = self.count_file_tokens(path)
            if file_result:
                result.add_file(file_result)
            return result

        # Walk directory tree
        for root, dirs, files in os.walk(path):
            root_path = Path(root)

            # Filter out ignored directories in-place
            dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d)]

            for filename in files:
                file_path = root_path / filename

                if self.should_ignore(file_path):
                    continue

                file_result = self.count_file_tokens(file_path)
                if file_result:
                    result.add_file(file_result)

        return result

    def scan_with_progress(
        self,
        path: Path,
        progress_callback: Optional[Callable[[Path, int, int], None]] = None,
    ) -> ScanResult:
        """
        Scan with optional progress callback.

        Args:
            path: Root directory to scan
            progress_callback: Called with (current_file, total_so_far)

        Returns:
            ScanResult with aggregated token counts
        """
        result = ScanResult()

        if not path.exists():
            return result

        # Collect all files first
        all_files: list[Path] = []

        if path.is_file():
            all_files = [path]
        else:
            for root, dirs, files in os.walk(path):
                root_path = Path(root)
                dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d)]

                for filename in files:
                    file_path = root_path / filename
                    if not self.should_ignore(file_path):
                        all_files.append(file_path)

        # Process files
        for i, file_path in enumerate(all_files):
            file_result = self.count_file_tokens(file_path)
            if file_result:
                result.add_file(file_result)

            if progress_callback:
                progress_callback(file_path, i + 1, len(all_files))

        return result
