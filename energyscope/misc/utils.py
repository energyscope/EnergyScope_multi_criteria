import os

# TODO: comment
# Useful functions for printing in AMPL syntax #
def make_dir(path):
    """
    Create the directory if it does not exist.
    """
    if not os.path.isdir(path):
        os.mkdir(path)
