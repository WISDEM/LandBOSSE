import os
import sys
from datetime import datetime
from shutil import copy2


class XlsxFileOperations:
    """
    This class is made to handle file naming and copying.
    """

    def __init__(self):
        """
        The __init__() method just makes a timestamp that will be used throughout
        the lifetime of this instance.
        """
        dt = datetime.now()
        self.timestamp = f'{dt.year}-{dt.month}-{dt.day}-{dt.hour}-{dt.minute}-{dt.second}'

    def get_input_output_paths_from_argv_or_env(self):
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

    def landbosse_input_dir(self):
        """
        See the get_input_output_paths_from_argv_or_env() function above. This
        function is simply a wrapper around that function to get the input
        path.

        Returns
        -------
        str
            The input directory.
        """
        input_path, _ = self.get_input_output_paths_from_argv_or_env()
        return input_path

    def landbosse_output_dir(self):
        """
        See the get_input_output_paths_from_argv_or_env() function above. This
        method gets the base path from there. Then, it checks for a timestamped
        directory that matches the timestamp in this instance. If it finds that
        directory, it simply returns the path to that directory. If it does
        not find that directory, it creates the directory and returns the path
        to the newly created directory.

        Returns
        -------
        str
            The output directory.
        """
        _, output_base_path = self.get_input_output_paths_from_argv_or_env()
        output_path = os.path.join(output_base_path, f'landbosse-{self.timestamp}')

        if os.path.exists(output_path) and not os.path.isdir(output_path):
            raise FileExistsError(f'Cannot overwrite {output_path} with LandBOSSE data.')
        elif not os.path.exists(output_path):
            os.mkdir(output_path)
            return output_path
        else:
            return output_path

    def copy_input_data(self):
        """
        This copies all input data including:

        - project_list.xlsx
        - everything under project_data/
        """
        src_project_list_xlsx = os.path.join(self.landbosse_input_dir(), 'project_list.xlsx')
        dst_project_list_xlsx = os.path.join(self.landbosse_output_dir(), 'project_list.xlsx')
        copy2(src_project_list_xlsx, dst_project_list_xlsx)

    def timestamp_filename(self, directory, basename, extension):
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
        filename = '{}-{}.{}'.format(basename, self.timestamp, extension)
        result = os.path.join(directory, filename)
        return result
