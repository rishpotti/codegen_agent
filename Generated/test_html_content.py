import pytest
from default_api import read_file

def test_html_file_content():
    expected_html_content = """<!DOCTYPE html>
<html>
<head>
<title>Yellow Background</title>
</head>
<body style="background-color:yellow;">

<h1>This page has a yellow background!</h1>

</body>
</html>"""
    # Assuming the HTML content is in a file named 'index.html' in the current directory
    # This test reads the content of 'index.html' and compares it with the expected HTML.
    # If 'index.html' does not exist or has different content, this test will fail.
    try:
        file_content_response = read_file(file_path='index.html')
        actual_html_content = file_content_response['content']
        assert actual_html_content == expected_html_content
    except Exception as e:
        pytest.fail(f"Could not read 'index.html' or an error occurred: {e}")
