import os
from datetime import datetime
import csv

import pandas as pd
from sympy import false

from landbosse.excelio import XlsxSerialManagerRunner
from landbosse.excelio import XlsxParallelManagerRunner
from landbosse.excelio import XlsxGenerator
from landbosse.excelio import XlsxValidator
from landbosse.excelio import CsvGenerator

# LandBOSSE, small utility functions
from landbosse.excelio import XlsxFileOperations
set_path = True
if set_path:
    input_output_path = '~/Desktop/'
    os.environ["LANDBOSSE_INPUT_DIR"] = input_output_path
else:
    input_output_path = os.path.dirname(__file__)
    os.environ["LANDBOSSE_INPUT_DIR"] = input_output_path


if __name__ == '__main__':
    # Print start timestamp
    print(f'>>>>>>>> Begin run {datetime.now()} <<<<<<<<<<')

    # The file_ops object handles file names for input and output data.
    file_ops = XlsxFileOperations()

    # If run_parallel is True, an XlsxParallelManagerRunner will calculate the
    # projects in parallel. This takes advantage of multicore architecture
    # available on most hardware.
    #
    # If run_parallel is False, XlsxSerialManagerRunner will calculate projects
    # serially. This is much slower so running in parallel is preferred
    # unless there is a good reason to run serially. One such reason is using a
    # debugger which can slow down when it is being used to debug multiple
    # processes.

    run_parallel = False
    manager_runner = XlsxParallelManagerRunner(file_ops) if run_parallel else XlsxSerialManagerRunner(file_ops)

    # project_xlsx is the absolute path of the project_list.xlsx
    projects_xlsx = os.path.join(file_ops.landbosse_input_dir(), 'project_list.xlsx')

    # Should we enable the scaling study? Just look for the scaling study
    # option. The first three elements of the returned tuple aren't necessary
    # to determine if the scaling study is enabled.
    # Switch to either validation or non validation producing code.
    input_path, output_path, validation_enabled, enable_scaling_study = file_ops.get_input_output_paths_from_argv_or_env()

    # final_result aggregates all the results from all the projects.
    final_result = manager_runner.run_from_project_list_xlsx(projects_xlsx, enable_scaling_study)
    # print(final_result)
    with open('/Users/pbhaskar/Desktop/dict.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in final_result.items():
            writer.writerow([key, value])

    # returns an exit code of either 0 (successful validation), or 1 (validation failed).
    #
    # If validation was not enabled, exit with a status of 0 (no errors)

    if validation_enabled:
        exit(build_status)
    else:
        exit(0)
