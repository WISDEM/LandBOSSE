import math
import numpy as np

class CostModule:
    """
    This is a super class for all other cost modules to import
    that provides shared methods for outputs from results and
    mobilization cost calculations.
    """

    def layout_length(self):
        """ In manual mode, calculates the total length between nodes in the farm, which is the road length, and cable
        length from substation to all turbines [km]."""
        self.output_dict['layout_length_km'] = 0
        self.collection_layout = self.input_dict['collection_layout'].values
        self.L = self.collection_layout[:, :2]  # location of nodes [m]
        self.A = self.collection_layout[:, 2:]  # adjacency matrix for collection system. Zeroth element is substation
        dim = self.A.shape
        self.n_segments = dim[1] - 1  # #turbines
        remains = np.ones(self.n_segments + 1)  # turbines still to have cables defined around
        for i in range(0, self.n_segments):
            for j in np.where(self.A[i, :] * remains == 1)[0]:
                self.output_dict['layout_length_km'] += ((self.L[i, 0] - self.L[j, 0]) ** 2 + (
                        self.L[i, 1] - self.L[j, 1]) ** 2) ** (1 / 2)
            remains[i] = False  # prevent duplicate cables

    def mobilization_cost(self, turbine_rating):
        """
        Calculates a mobilization cost term as a function of
        turbine rating.

        Parameters
        ----------
        turbine_rating : float
            Turbine rating in megawatts

        Returns
        -------
        float
            The mobilization cost as a function of turbine rating.
        """

        mobilization_cost = (36.892 * math.exp(-5e-04 * (turbine_rating * 1000))) / 100
        return mobilization_cost

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
            True if the cost is total for the project. False if it
            is per turbine.

        Returns
        -------
        list
            List of dicts, with each dict representing a row for
            the output.
        """
        result = []
        # module = type(self).__name__
        module = 'CollectionCost' if (type(self).__name__ == 'ArraySystem') else type(self).__name__
        turbine_rating_MW = self.input_dict['turbine_rating_MW']
        num_turbines = self.input_dict['num_turbines']
        rotor_diameter_m = self.input_dict['rotor_diameter_m']
        project_size_kw = num_turbines * turbine_rating_MW * 1000

        for _, row in input_df.iterrows():
            _dict = dict()
            row = row.to_dict()
            _dict['operation_id'] = row['Phase of construction']
            _dict['type_of_cost'] = row['Type of cost']
            _dict['raw_cost'] = row['Cost USD']
            result.append(_dict)

        for _dict in result:
            _dict['turbine_rating_MW'] = turbine_rating_MW
            _dict['num_turbines'] = num_turbines
            _dict['rotor_diameter_m'] = rotor_diameter_m
            _dict['project_id_with_serial'] = self.project_name
            _dict['module'] = module

            if total_or_turbine:  # If raw_cost is the total cost
                _dict['raw_cost_total_or_per_turbine'] = 'total'
                _dict['cost_per_turbine'] = _dict['raw_cost'] / num_turbines
                _dict['cost_per_project'] = _dict['raw_cost']
                _dict['usd_per_kw_per_project'] = _dict['raw_cost'] / project_size_kw
            else:                 # If raw_cost is per turbine
                _dict['raw_cost_total_or_per_turbine'] = 'turbine'
                _dict['cost_per_turbine'] = _dict['raw_cost']
                _dict['cost_per_project'] = _dict['raw_cost'] * num_turbines
                _dict['usd_per_kw_per_project'] = _dict['cost_per_project'] / project_size_kw

        return result
