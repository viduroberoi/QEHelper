from argparse import ArgumentTypeError

import pytest

from qehelper.cli import read_requirement_file


def test_read_requirement_file_accepts_markdown(tmp_path) -> None:
    requirement_file = tmp_path / "password-reset.md"
    requirement_file.write_text("# Password reset\n\nSend reset links by email.\n", encoding="utf-8")
    assert read_requirement_file(requirement_file) == "# Password reset\n\nSend reset links by email."


def test_read_requirement_file_rejects_other_extensions(tmp_path) -> None:
    requirement_file = tmp_path / "requirements.pdf"
    requirement_file.write_bytes(b"not a real PDF")
    with pytest.raises(ArgumentTypeError, match=".md"):
        read_requirement_file(requirement_file)


def test_read_requirement_file_rejects_empty_file(tmp_path) -> None:
    requirement_file = tmp_path / "requirements.txt"
    requirement_file.write_text(" \n", encoding="utf-8")
    with pytest.raises(ArgumentTypeError, match="empty"):
        read_requirement_file(requirement_file)
