import os
from datetime import datetime

from landbosse.excelio import XlsxSerialManagerRunner
from landbosse.excelio import XlsxParallelManagerRunner
from landbosse.excelio import XlsxGenerator
from landbosse.excelio import XlsxValidator

# LandBOSSE, small utility functions
from landbosse.excelio import XlsxFileOperations

if __name__ == '__main__':
    # Print start timestamp
    print(f'>>>>>>>> Begin run {datetime.now()} <<<<<<<<<<')

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
    manager_runner = XlsxParallelManagerRunner() if run_parallel else XlsxSerialManagerRunner()

    # The file_ops object handles file names for input and output data.
    file_ops = XlsxFileOperations()

    # project_xlsx is the absolute path of the project_list.xlsx
    projects_xlsx = os.path.join(file_ops.landbosse_input_dir(), 'project_list.xlsx')

    # final_result aggregates all the results from all the projects.
    final_result = manager_runner.run_from_project_list_xlsx(projects_xlsx)

    # Write the enhanced_project_list, which has all the parametric values.
    enhanced_project_list_path = os.path.join(file_ops.landbosse_output_dir(), 'enhanced_project-list.xlsx')
    enhanced_project_list = final_result['enhanced_project_list']
    enhanced_project_list.to_excel(enhanced_project_list_path, index=False)

    # Switch to either validation or non validation producing code.
    input_path, output_path, validation_enabled = file_ops.get_input_output_paths_from_argv_or_env()

    # Run validation or not depending on whether validation was enabled.
    if validation_enabled:
        print('Running validation.')

        # Creates file path for output file from prior LandBOSSE run that will be used to check latest run
        # Generated based on input_path from command line when --validate option is specified
        # (validation output file must be in inputs folder and must be called 'landbosse-output-validation.xlsx')
        expected_validation_data_path = os.path.join(input_path, 'landbosse-expected-validation-data.xlsx')
        validation_result_path = os.path.join(file_ops.landbosse_output_dir(), 'landbosse-validation-result.xlsx')

        validator = XlsxValidator()
        validation_was_successful = validator.compare_expected_to_actual(
            expected_xlsx=expected_validation_data_path,
            actual_module_type_operation_list=final_result['module_type_operation_list'],
            validation_output_xlsx=validation_result_path
        )
        if validation_was_successful:
            print('Validation passed.')
        else:
            print('Validation failed. See mismatched data above.')

    # XlsxGenerator has a context manager that writes each individual
    # worksheet to the output .xlsx. Also, copy file input structure.
    print('Writing final output folder')
    with XlsxGenerator('landbosse-output', file_ops) as xlsx:
        xlsx.tab_costs_by_module_type_operation(rows=final_result['module_type_operation_list'])
        xlsx.tab_details(rows=final_result['details_list'])
    file_ops.copy_input_data()

    # Print end timestamp
    print(f'>>>>>>>> End run {datetime.now()} <<<<<<<<<<')
