class SharedOutputMixin:
    """
    This is a mixin for shared code among modules that create output for
    spreadsheets and other reports.
    """

    def outputs_for_costs_by_module_type_operation(self,
                                                   *,
                                                   input_df,
                                                   project_id,
                                                   total_or_turbine):
        """
        This takes a dataframe and turns it into a list of dictionaries
        suitable for output to a cost tab in a spreadsheet.

        Outputs dictionaries that are rows, with each row being a dict that
        has costs broken down by and module id, operation id, type of cost,
        cost, and per turbine or total. Each of those values are stored in
        their own column.

        It maps each row of this dataframe into a dictionary with keys
        of those names. It accumulates these dictionaries into a list.

        It must be called with keyword arguments.

        Parameters
        ----------
        input_df : pd.DataFrame
           The input dataframe that has the columns listed above.

        project_id : str
            The id of the project (it is a string, not an integer) to
            place in each row.

        total_or_turbine : bool
            True if the cost is per turbine. False if it is total
            in the project.

        Returns
        -------
        list
            List of dicts, with each dict representing a row for
            the output.
        """
        result = []
        # module = type(self).__name__
        module = 'CollectionCost' if (type(self).__name__ == 'ArraySystem') else type(self).__name__

        for _, row in input_df.iterrows():
            _dict = dict()
            row = row.to_dict()
            _dict['operation_id'] = row['Phase of construction']
            _dict['type_of_cost'] = row['Type of cost']
            _dict['cost'] = row['Cost USD']
            result.append(_dict)

        for _dict in result:
            _dict['project_id'] = project_id
            _dict['module'] = module
            _dict['total_or_turbine'] = 'total' if total_or_turbine else 'turbine'

        return result