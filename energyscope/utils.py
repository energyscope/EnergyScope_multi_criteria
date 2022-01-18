import os

# TODO: remove ?
def make_dir(path: str):
    """Create the directory if it does not exist."""
    if not os.path.isdir(path):
        os.mkdir(path)
