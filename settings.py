import json
import os


global settings


def load_settings(path):
    current_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(current_dir, path)) as f:
        global settings
        settings = json.load(f)
