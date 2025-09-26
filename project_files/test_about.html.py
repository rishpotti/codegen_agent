import unittest
import os

class TestAboutHtml(unittest.TestCase):
    def test_about_html_exists(self):
        # Assuming about.html is in the same directory as the test runner or a known path relative to the sandbox
        # For simplicity, we'll assume it's in the root of the sandbox or accessible.
        # If 'about.html' is meant to be in 'project_files', the path below would need adjustment.
        # Given the error for 'project_files\test_about.html.py', it's possible 'about.html' is also in 'project_files'.
        # For now, we'll check for 'about.html' in the current working directory of the test.
        # A more robust test would specify the exact expected path of about.html.
        file_path = "about.html"
        self.assertTrue(os.path.exists(file_path), f"File {file_path} does not exist.")

if __name__ == '__main__':
    unittest.main()