import os

# Define the base directory relative to the current file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the relative path to the templates directory
TEMPLATE_DIR = os.path.join(BASE_DIR, 'files', 'templates')
