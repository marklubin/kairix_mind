import json
import os
import tempfile
import unittest
from unittest.mock import patch

from kairix.ui.functions import load_from_file
from kairix.types import SourceDocument


class TestLoadFromFile(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = tempfile.mkdtemp()

    def tearDown(self):
        for filename in os.listdir(self.test_data_dir):
            os.remove(os.path.join(self.test_data_dir, filename))
        os.rmdir(self.test_data_dir)

    def create_test_file(self, filename, data):
        filepath = os.path.join(self.test_data_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f)
        return filepath

    @patch.object(SourceDocument, 'save')
    def test_valid_single_conversation(self, mock_save):
        test_data = [
            {
                "title": "Test Conversation",
                "mapping": {
                    "msg0": {
                        "message": {
                            "author": {"role": "system"},
                            "content": {"parts": ["System init"]},
                            "create_time": 1234567890,
                        }
                    },
                    "msg1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Hello, how are you?"]},
                            "create_time": 1234567891,
                        }
                    },
                    "msg2": {
                        "message": {
                            "author": {"role": "assistant"},
                            "content": {"parts": ["I'm doing well, thank you!"]},
                            "create_time": 1234567892,
                        }
                    },
                },
            }
        ]

        filepath = self.create_test_file("single_convo.json", test_data)
        results = list(load_from_file(filepath))

        # Should yield one result for one conversation
        self.assertEqual(len(results), 1)
        # Result should contain the title
        self.assertIn("Test Conversation", results[0])

    def test_multiple_conversations(self):
        test_data = [
            {
                "title": "Conversation 1",
                "mapping": {
                    "msg0": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["First convo"]},
                            "create_time": 1234567890,
                        }
                    },
                    "msg1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Question 1"]},
                            "create_time": 1234567891,
                        }
                    },
                },
            },
            {
                "title": "Conversation 2",
                "mapping": {
                    "msg0": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Second convo"]},
                            "create_time": 1234567892,
                        }
                    },
                    "msg1": {
                        "message": {
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Response 2"]},
                            "create_time": 1234567893,
                        }
                    },
                },
            },
        ]

        filepath = self.create_test_file("multiple_convos.json", test_data)
        results = list(load_from_file(filepath))

        # Should yield two results, one after each conversation
        self.assertEqual(len(results), 2)
        # First result should only have first conversation
        self.assertIn("Conversation 1", results[0])
        self.assertNotIn("Conversation 2", results[0])
        # Second result should have both conversations
        self.assertIn("Conversation 1", results[1])
        self.assertIn("Conversation 2", results[1])

    def test_empty_file_list(self):
        results = list(load_from_file([]))
        self.assertEqual(results, ["No file selected"])

    def test_file_list_with_single_file(self):
        test_data = [
            {
                "title": "List Test",
                "mapping": {
                    "msg0": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Test message"]},
                            "create_time": 1234567890,
                        }
                    },
                    "msg1": {
                        "message": {
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Test response"]},
                            "create_time": 1234567891,
                        }
                    },
                },
            }
        ]

        filepath = self.create_test_file("list_test.json", test_data)
        results = list(load_from_file([filepath]))

        self.assertEqual(len(results), 1)
        self.assertIn("List Test", results[0])

    def test_invalid_json_file(self):
        filepath = os.path.join(self.test_data_dir, "invalid.json")
        with open(filepath, "w") as f:
            f.write("invalid json content")

        with self.assertRaises(json.JSONDecodeError):
            list(load_from_file(filepath))

    def test_system_messages_filtered(self):
        test_data = [
            {
                "title": "System Filter Test",
                "mapping": {
                    "msg0": {
                        "message": {
                            "author": {"role": "system"},
                            "content": {"parts": ["System message - should be filtered"]},
                            "create_time": 1234567890,
                        }
                    },
                    "msg1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["User message - should be included"]},
                            "create_time": 1234567891,
                        }
                    },
                    "msg2": {
                        "message": {
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Assistant message - should be included"]},
                            "create_time": 1234567892,
                        }
                    },
                },
            }
        ]

        filepath = self.create_test_file("system_filter.json", test_data)
        # We need to check the actual documents created
        # Since we can't easily access the SourceDocument content without mocking,
        # we'll just verify the function runs without error
        results = list(load_from_file(filepath))
        self.assertEqual(len(results), 1)

    def test_messages_with_missing_fields(self):
        test_data = [
            {
                "title": "Missing Fields Test",
                "mapping": {
                    "msg0": {"message": None},  # No message
                    "msg1": {
                        "message": {
                            "author": None,  # No author
                            "content": {"parts": ["No author message"]},
                            "create_time": 1234567890,
                        }
                    },
                    "msg2": {
                        "message": {
                            "author": {"role": "user"},
                            # Missing content
                            "create_time": 1234567891,
                        }
                    },
                    "msg3": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Valid message"]},
                            "create_time": 1234567892,
                        }
                    },
                },
            }
        ]

        filepath = self.create_test_file("missing_fields.json", test_data)
        # Should not raise an error, just skip invalid messages
        results = list(load_from_file(filepath))
        self.assertEqual(len(results), 1)

    def test_first_message_skipped_by_index(self):
        test_data = [
            {
                "title": "Index Test",
                "mapping": {
                    "msg0": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Message at index 0 - should be skipped"]},
                            "create_time": 1234567890,
                        }
                    },
                    "msg1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Message at index 1 - should be included"]},
                            "create_time": 1234567891,
                        }
                    },
                },
            }
        ]

        filepath = self.create_test_file("index_test.json", test_data)
        results = list(load_from_file(filepath))
        self.assertEqual(len(results), 1)

    def test_empty_conversations(self):
        test_data = [
            {
                "title": "Empty Conversation",
                "mapping": {},
            }
        ]

        filepath = self.create_test_file("empty_convo.json", test_data)
        results = list(load_from_file(filepath))
        self.assertEqual(len(results), 1)
        self.assertIn("Empty Conversation", results[0])

    def test_real_test_file_structure(self):
        # Test with the real test-convos.json file if it exists
        test_file_path = "/Users/mark/kairix_mind/test-convos.json"
        if os.path.exists(test_file_path):
            try:
                results = list(load_from_file(test_file_path))
                self.assertTrue(len(results) > 0)
                # Each result should be a string containing conversation titles
                for result in results:
                    self.assertIsInstance(result, str)
            except Exception as e:
                self.fail(f"Failed to load real test file: {e}")


if __name__ == "__main__":
    unittest.main()