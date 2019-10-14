import os
import sys
from datetime import datetime


class XlsxFileOperations:
    """
    This class has methods to find, name and copy files. It is not meant
    to be instantiated. All the methods are class methods and are held
    in this class for organization.
    """

    @classmethod
    def get_input_output_paths_from_argv_or_env(cls):
        """
        This uses the sys.argv object to inspect the command line to find input
        and output paths as specified on the command line. It expects the
        command line to have options in the following form:

        -i [input file] -o [output file]

        If one or both of these is missing, then it is filled with the defaults
        from the environment variables LANDBOSSE_INPUT_DIR or LANDBOSSE_OUTPUT_DIR

        If all of them are missing the method defaults to 'inputs/' and 'outputs/'

        Parameters
        ----------
        This function takes no parameters.

        Returns
        -------
        str, str
            The paths for input and output, repectively. These paths aren't checked
            for validity.
        """

        # Get the fallback paths from the environment variables and set their
        # defaults. These defualts are used

        input_path_from_env = os.environ.get('LANDBOSSE_INPUT_DIR', 'input')
        output_path_from_env = os.environ.get('LANDBOSSE_OUTPUT_DIR', 'output')

        # input and output paths from command line are initially set to None
        # to indicate they have not been found yet.

        input_path_from_arg = None
        output_path_from_arg = None

        # Look for the input path on command line
        if '--input' in sys.argv and sys.argv.index('--input') + 1 < len(sys.argv):
            input_idx = sys.argv.index('--input') + 1
            input_path_from_arg = sys.argv[input_idx]

        if '-i' in sys.argv and sys.argv.index('-i') + 1 < len(sys.argv):
            input_idx = sys.argv.index('-i') + 1
            input_path_from_arg = sys.argv[input_idx]

        # Look for the output path on command line
        if '--output' in sys.argv and sys.argv.index('--output') + 1 < len(sys.argv):
            output_idx = sys.argv.index('--output') + 1
            output_path_from_arg = sys.argv[output_idx]

        if '-o' in sys.argv and sys.argv.index('-o') + 1 < len(sys.argv):
            output_idx = sys.argv.index('-o') + 1
            output_path_from_arg = sys.argv[output_idx]

        # Find the final input and output paths. If a command line argument was
        # found for input and/or output, that is used. If it wasn't found,
        # the value from the environment variable search is returned, which includes
        # the default if the environment variable itself wasn't found.

        input_path = input_path_from_arg if input_path_from_arg is not None else input_path_from_env
        output_path = output_path_from_arg if output_path_from_arg is not None else output_path_from_env

        return input_path, output_path

    @classmethod
    def landbosse_output_dir(cls):
        """
        See the get_input_output_paths_from_argv_or_env() function above. This
        function is simply a wrapper around that function to get the output
        path.

        Returns
        -------
        str
            The output directory.
        """
        _, output_path = cls.get_input_output_paths_from_argv_or_env()
        return output_path

    @classmethod
    def landbosse_input_dir(cls):
        """
        See the get_input_output_paths_from_argv_or_env() function above. This
        function is simply a wrapper around that function to get the input
        path.

        Returns
        -------
        str
            The input directory.
        """
        input_path, _ = cls.get_input_output_paths_from_argv_or_env()
        return input_path

    @classmethod
    def timestamp_filename(cls, directory, basename, extension):
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
