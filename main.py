import os

from landbosse.excelio import XlsxSerialManagerRunner
from landbosse.excelio import XlsxParallelManagerRunner
from landbosse.excelio import XlsxGenerator

# LandBOSSE, small utility functions
from landbosse.excelio import landbosse_input_dir

if __name__ == '__main__':
    # If run_parallel is True, an XlsxParallelManagerRunner will calculate the
    # projects in parallel. This takes advantage of multicore architecture
    # available on most hardware.
    #
    # If run_parallel is False, XlsxSerialManagerRunner will calculate projects
    # serially. This is much slower so running in parallel is preferred
    # unless there is a good reason to run serially. One such reason is using a
    # debugger which can slow down when it is being used to debug multiple
    # processes.

    run_parallel = True
    manager_runner = XlsxParallelManagerRunner() if run_parallel else XlsxSerialManagerRunner()
    projects_xlsx = os.path.join(landbosse_input_dir(), 'project_list.xlsx')

    final_result = manager_runner.run_from_project_list_xlsx(projects_xlsx)

    with XlsxGenerator('landbosse-output') as xlsx:
        xlsx.tab_costs_by_module_type_operation(rows=final_result['module_type_operation_list'])
        xlsx.tab_details(rows=final_result['details_list'])
