import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import pandas as pd
import numpy as np
import os
import traceback

from .filename_functions import timestamp_filename
from .filename_functions import landbosse_output_dir
from .filename_functions import landbosse_input_dir


class XlsxGenerator:
    """
    This class is for writing data to Excel files. It is a context manager
    so it used in the following manner:

    with XlsxGenerator(output_xlsx) as xlsx:
        xlsx.joined_with_validation(...)

    Each method call on the context manager makes one or more tabs on the
    output Excel workbook.
    """

    def __init__(self, output_xlsx):
        """
        This constructor sets the name of the .xlsx file for writing

        It sets the parameter self.workbook, which is the attribute that
        references the workbook to which all tabs should be written.

        Parameters
        ----------
        output_xlsx : str
            The name of the .xlsx file to write. Do not include the .xlsx at
            the end of the filename. Also, this filename will be timestamped
            before it is written.
        """

        # Set all instance attributes to None first in the constructor as good
        # coding practice.
        self.workbook = None
        self.header_format = None
        self.scientific_format = None
        self.percent_format = None
        self.output_xlsx_path = timestamp_filename(landbosse_output_dir(), output_xlsx, 'xlsx')

    def __enter__(self):
        """
        Opens the workbook for writing and sets the formatting.

        Returns
        -------
        self
            Returns self for easy use in the context manager.
        """
        self.workbook = xlsxwriter.Workbook(self.output_xlsx_path, {'nan_inf_to_errors': True})
        self.set_workbook_formats()
        return self

    def __exit__(self, exception_type, exception_val, exception_traceback):
        """
        Closes the workbook

        Parameters
        ----------
        exception_type
            The type of the exception, if there is one.
        exception_val
            The value of the exception, if there is one.
        exception_traceback
            Traceback of the exception problem.

        Returns
        -------
        bool
            True if the workbook is closed properly. False if something
            prevented normal closure.
        """
        if exception_type:
            print('exception_type: {}'.format(exception_type))
            print('exception_val: {}'.format(exception_val))
            print('exception_traceback:')
            traceback.print_tb(exception_traceback)
        self.workbook.close()
        return True

    def set_workbook_formats(self):
        """
        This method creates the formats in the workbook. It is called upon entry
        into the context manager.
        """
        self.header_format = self.workbook.add_format()
        self.header_format.set_bold()
        self.header_format.set_text_wrap()
        self.scientific_format = self.workbook.add_format()
        self.scientific_format.set_num_format('0.00E+00')
        self.scientific_format.set_align('left')
        self.percent_format = self.workbook.add_format()
        self.percent_format.set_num_format('0.0%')
        self.percent_format.set_align('left')
        self.accounting_format = self.workbook.add_format()
        self.accounting_format.set_num_format('$ #,##0')

    def tab_costs_by_module_type_operation(self, rows):
        """
        This writes the costs_by_module_type_operation tab.

        Parameters
        ----------
        rows : list
            List of dictionaries that are each row in the output
            sheet.
        """
        worksheet = self.workbook.add_worksheet('costs_by_module_type_operation')
        for idx, col_name in enumerate(['project_id', 'module', 'operation_id', 'type_of_cost', 'total_or_turbine', 'cost']):
            worksheet.write(0, idx, col_name, self.header_format)
        for row_idx, row in enumerate(rows):
            worksheet.write(row_idx + 1, 0, row['project_id'])
            worksheet.write(row_idx + 1, 1, row['module'])
            worksheet.write(row_idx + 1, 2, row['operation_id'])
            worksheet.write(row_idx + 1, 3, row['type_of_cost'])
            worksheet.write(row_idx + 1, 4, row['total_or_turbine'])
            worksheet.write(row_idx + 1, 5, row['cost'], self.accounting_format)
            worksheet.set_column(0, 5, 25)
        worksheet.freeze_panes(1, 0)  # Freeze the first row.

    def tab_details(self, rows):
        """
        This writes a detailed outputs tab. It takes a list of dictionaries
        as the parameters and in each of those dictionaries it looks at the keys:

        ['project_id', 'module', 'type', 'variable_df_key_col_name', 'unit', 'value']

        The values of each of those keys become each cell in the row.

        Parameters
        ----------
        rows : list
            list of dicts. See above.

        Returns
        -------
        str
            The string of the full pathname to the file just written.
        """
        worksheet = self.workbook.add_worksheet('details')
        worksheet.set_column(3, 3, 66)
        worksheet.set_column(4, 4, 17)
        worksheet.set_column(5, 5, 66)
        worksheet.set_column(0, 2, 17)
        for idx, col_name in enumerate(['project_id', 'module', 'type', 'variable_df_key_col_name', 'unit', 'value', 'last number']):
            worksheet.write(0, idx, col_name, self.header_format)
        for row_idx, row in enumerate(rows):
            worksheet.write(row_idx + 1, 0, row['project'])
            worksheet.write(row_idx + 1, 1, row['module'])
            worksheet.write(row_idx + 1, 2, row['type'])
            worksheet.write(row_idx + 1, 3, row['variable_df_key_col_name'])
            worksheet.write(row_idx + 1, 4, row['unit'])
            if type(row['value']) is str or type(row['value']) is int or type(row['value']) is float:
                worksheet.write(row_idx + 1, 5, row['value'], self.scientific_format)
            else:
                worksheet.write(row_idx + 1, 5, str(row['value']))
            if 'last_number' in row:
                if type(row['last_number']) is int or type(row['last_number']) is float:
                    worksheet.write(row_idx + 1, 6, row['last_number'], self.scientific_format)
                else:
                    worksheet.write(row_idx + 1, 6, str(row['last_number']))
        worksheet.freeze_panes(1, 0)  # Freeze the first row.

    def tab_details_with_validation(self, rows, validation_xlsx):
        """
        This is a special method that is for validation only. If you
        just need the details tab, use the tab_details() method.

        This writes an .xlsx file. It takes a list of dictionaries as the parameter
        and in each of those dictionaries it looks at the keys:

        ['project_id', 'module', 'type', 'variable_df_key_col_name', 'unit', 'value']

        as the order of columns for each row of the .xlsx file.

        It also sets up some number and text formatting and column widths for
        the .xlsx file.

        It timestamps the output filename of the output xlsx.

        Parameters
        ----------
        rows : list
            list of dicts. See above.

        validation_xlsx : str
            The name of .xlsx file which contains the validation data. It is
            assumed to live in the inputs directory. Please include .xlsx

        Returns
        -------
        str
            The string of the full pathname to the file just written.
        """
        # Read the validation inputs. Validation data assumed to be on 'Sheet1'
        validation_xlsx_path = os.path.join(landbosse_input_dir(), validation_xlsx)
        validation = pd.read_excel(validation_xlsx_path, 'Sheet1')
        validation_row_dicts = [row.to_dict() for _, row in validation.iterrows()]

        # Make a worksheet for the model outputs
        worksheet = self.workbook.add_worksheet('details')

        # Write values to the output spreadsheet.
        for idx, col_name in enumerate(['Project ID', 'module', 'type', 'variable_df_key_col_name', 'unit', 'value', 'last_number', 'expected_value', 'difference', 'primary_key']):
            worksheet.write(0, idx, col_name, self.header_format)
        row_idx = 1
        for row in rows:
            pk_part_1_cell = xl_rowcol_to_cell(row_idx, 0)
            pk_part_2_cell = xl_rowcol_to_cell(row_idx, 3)
            value_cell = xl_rowcol_to_cell(row_idx, 6) if 'last_number' in row else xl_rowcol_to_cell(row_idx, 5)
            expected_value_cell = xl_rowcol_to_cell(row_idx, 7)
            worksheet.write(row_idx, 0, row['project'])
            worksheet.write(row_idx, 1, row['module'])
            worksheet.write(row_idx, 2, row['type'])
            worksheet.write(row_idx, 3, row['variable_df_key_col_name'])
            worksheet.write(row_idx, 4, row['unit'])

            if type(row['value']) is int or type(row['value']) is float:
                worksheet.write(row_idx, 5, row['value'], self.scientific_format)
            else:
                worksheet.write(row_idx, 5, str(row['value']))
            if 'last_number' in row:
                if type(row['last_number']) is int or type(row['last_number']) is float:
                    worksheet.write(row_idx, 6, row['last_number'], self.scientific_format)
                else:
                    worksheet.write(row_idx, 6, str(row['last_number']))

            f = '=INDEX(details_validation!$C$2:$C${}, MATCH(details!J{}, details_validation!$J$2:$J${}, 0))'.format(len(validation_row_dicts) + 1, row_idx + 1, len(validation_row_dicts) + 1)
            worksheet.write(row_idx, 7, f, self.scientific_format)

            worksheet.write(row_idx, 8, '={}/{}'.format(expected_value_cell, value_cell), self.percent_format)
            worksheet.write_formula(row_idx, 9, '=CONCATENATE({}, {})'.format(pk_part_1_cell, pk_part_2_cell))
            row_idx += 1
        worksheet.freeze_panes(1, 0)  # Freeze the first row.

        # Write the validation outputs to a tab in the excel file. Make the primary key
        worksheet = self.workbook.add_worksheet('details_validation')
        validations_col_names = list(validation_row_dicts[0].keys())[:]
        validations_col_names.append('primary_key')
        for idx, col_name in enumerate(validations_col_names):
            worksheet.write(0, idx, col_name, self.header_format)
            worksheet.set_column(idx, idx, 50)
        row_idx = 1
        for row in validation_row_dicts:
            pk_part_1_cell = xl_rowcol_to_cell(row_idx, 0)
            pk_part_2_cell = xl_rowcol_to_cell(row_idx, 5)
            worksheet.write(row_idx, 0, row['Project ID'])
            worksheet.write(row_idx, 1, row['variable_name_validation_data'])
            worksheet.write(row_idx, 2, row['expected_value'])
            worksheet.write(row_idx, 3, row['module'])
            worksheet.write(row_idx, 4, row['type'])
            worksheet.write(row_idx, 5, row['variable_df_key_col_name'])
            worksheet.write(row_idx, 6, row['unit'])
            worksheet.write(row_idx, 7, row['value'])
            worksheet.write(row_idx, 8, row['notes'])
            worksheet.write(row_idx, 9, '=CONCATENATE({}, {})'.format(pk_part_1_cell, pk_part_2_cell))
            row_idx += 1
        worksheet.freeze_panes(1, 0)  # Freeze the first row.
