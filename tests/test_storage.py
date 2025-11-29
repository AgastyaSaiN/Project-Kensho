import unittest
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from src.kensho.storage import load_app_state, save_app_state, APP_STATE_FILENAME

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.sample_state = {"window": {"pinned": True}}

    @patch("src.kensho.storage.APP_STATE_FILE")
    @patch("src.kensho.storage.ensure_data_dir")
    def test_load_app_state_success(self, mock_ensure, mock_file_path):
        mock_file_path.exists.return_value = True
        
        # Mock the file opening and reading
        m = mock_open(read_data=json.dumps(self.sample_state))
        mock_file_path.open = m
        
        state = load_app_state()
        self.assertEqual(state, self.sample_state)
        mock_ensure.assert_called_once()

    @patch("src.kensho.storage.APP_STATE_FILE")
    @patch("src.kensho.storage.ensure_data_dir")
    def test_load_app_state_no_file(self, mock_ensure, mock_file_path):
        mock_file_path.exists.return_value = False
        
        state = load_app_state()
        self.assertEqual(state, {})

    @patch("src.kensho.storage.APP_STATE_FILE")
    @patch("src.kensho.storage.ensure_data_dir")
    def test_save_app_state(self, mock_ensure, mock_file_path):
        # Setup mock for temporary file
        mock_tmp = unittest.mock.MagicMock()
        mock_file_path.with_suffix.return_value = mock_tmp
        
        m = mock_open()
        mock_tmp.open = m
        
        save_app_state(self.sample_state)
        
        # Verify write
        handle = m()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(json.loads(written), self.sample_state)
        
        # Verify rename
        mock_tmp.replace.assert_called_with(mock_file_path)

if __name__ == '__main__':
    unittest.main()
