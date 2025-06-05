import sys, os

def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relative_path)
