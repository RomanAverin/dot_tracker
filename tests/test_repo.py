"""Module providing a unit testing functions."""
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
import os
import pathlib
import unittest
from unittest.mock import patch
import yaml

from src.dot_tracker.main import Config

fuxtures_dir = pathlib.Path(__file__).parent / "fixtures"


@contextmanager
def temp_repo(content):
    try:
        temp_file = NamedTemporaryFile("+w", delete=False)
        temp_file.write(content)
        temp_file.close()
        yield temp_file.name
    finally:
        os.unlink(temp_file.name)


class TestConf(unittest.TestCase):
    """Class of functions testing repository read, parce, write"""

    def test_read_repo(self):
        """Test parse YML to Config object"""
        with open("tests/fixtures/single_config.yml", "r", encoding="utf-8") as f:
            yml = {"name": "vim", "files": ["~/.vimrc", "~/.ohmyzsh"]}
            parsed_yaml = yaml.safe_load_all(f)

            # expected = Config("vim", ["~/.vimrc", "~/.ohmyzsh"])

            self.assertEqual(yml, next(parsed_yaml))


if __name__ == "__main__":
    unittest.main()
