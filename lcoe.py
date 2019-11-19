import pandas as pd

if __name__ == '__main__':
    aep = pd.read_csv('aep.csv')
    tcc = pd.read_csv('tcc.csv')
    aep_tcc = aep.merge(tcc, on=['Rating [kW]', 'Rotor Diam [m]'])

    landbosse_costs = pd.read_excel('landbosse-output.xlsx', 'costs_by_module_type_operation')
    landbosse_costs['Rating [kW]'] = landbosse_costs['Turbine rating MW'] * 1000
    landbosse_costs.rename(columns={'Rotor diameter m': 'Rotor Diam [m]'}, inplace=True)
    landbosse_costs.drop(columns=['Turbine rating MW', ''], inplace=True)

    landbosse_cost_sum = landbosse_costs.groupby(['Rating [kW]', 'Rotor Diam [m]', 'Number of turbines']).sum().reset_index()

    joined = aep_tcc.merge(landbosse_cost_sum, on=['Rating [kW]', 'Rotor Diam [m]'])

    with pd.ExcelWriter('lcoe_analysis.xlsx', mode='w') as writer:
        joined.to_excel(writer, sheet_name='Joined', index=False)
        landbosse_cost_sum.to_excel(writer, sheet_name='LandBOSSE Cost Sums', index=False)
        aep_tcc.to_excel(writer, sheet_name='AEP TCC', index=False)
        landbosse_costs.to_excel(writer, sheet_name='LandBOSSE Costs', index=False)
        aep.to_excel(writer, sheet_name='AEP', index=False)
        tcc.to_excel(writer, sheet_name='TCC', index=False)
