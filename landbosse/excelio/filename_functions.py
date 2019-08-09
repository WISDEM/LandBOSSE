import os
from datetime import datetime


"""
This module has functions to assist with filenaming for input
and output filenames.
"""


def landbosse_output_dir():
    """
    This function is to find the output directory in which to place
    output files from landbosse.

    This function checks to see if the LANDBOSSE_OUTPUT_DIR environment
    variable is defined. If so, it returns the value of that variable.

    If the environment variable is not defined, it returns 'outputs'
    relative to the current working directory.

    Returns
    -------
    str
        The output directory.
    """
    return os.environ['LANDBOSSE_OUTPUT_DIR'] if 'LANDBOSSE_OUTPUT_DIR' in os.environ else 'output'


def landbosse_input_dir():
    """
    This function is to find the input directory from which to read
    landbosse input files.

    This function checks to see if the LANDBOSSE_INPUT_DIR environment
    variable is defined. If so, it returns the value of that variable.

    If the environment variable is not defined, it returns 'inputs'
    relative to the current working directory.

    Returns
    -------
    str
        The input directory.
    """
    return os.environ['LANDBOSSE_INPUT_DIR'] if 'LANDBOSSE_INPUT_DIR' in os.environ else 'input'


def timestamp_filename(directory, basename, extension):
    """
    This function creates a timestamped filename. It uses a filename in the
    format of:

    basename-timestamp.extension

    And joins it to the directory specified by directory. It uses os.path.join()
    so it's OS independent.

    Parameters
    ----------
    directory : str
        The directory for this filename

    basename : str
        The filename without the timestamp or extension

    extension : str
        The last part of the filname, without the "."

    Returns
    -------
    str
        The path for the host operating system.
    """
    dt = datetime.now()
    timestamp = '{}-{}-{}-{}-{}-{}'.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    filename = '{}-{}.{}'.format(basename, timestamp, extension)
    result = os.path.join(directory, filename)
    return result
