import numpy as np
import itertools
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os

cwd = Path.cwd()
pawd = cwd.parent


FL_vec = np.arange(260, 361, 10)

fuel_nox_iter_var_vec = np.arange(0, 810, 1)
year_vec = np.arange(2040, 2140, 1)

fuel_and_emis_bounds_ip = [(-25, 60), (-100, 1000)]
fuel_and_emis_resolution_range_ip = [5, 25]

fuel_burn_percent_limits = fuel_and_emis_bounds_ip[0]
fuel_burn_range_resolution = fuel_and_emis_resolution_range_ip[0]

einox_percent_limits = fuel_and_emis_bounds_ip[1]
einox_range_resolution = fuel_and_emis_resolution_range_ip[1]

einox_factor_range = [float(round((1+(elem/100)), 4)) for elem in np.arange(einox_percent_limits[0], einox_percent_limits[1]+einox_range_resolution, einox_range_resolution)]
fuel_burn_factor_range = [float(round((1+(elem/100)), 4)) for elem in np.arange(fuel_burn_percent_limits[0], fuel_burn_percent_limits[1]+fuel_burn_range_resolution, fuel_burn_range_resolution)]

einox_factor_range[0] = 0.05
param_tuples_fuel_and_nox_var = list(itertools.product(fuel_burn_factor_range, einox_factor_range))

baseline_alt_results_folder = os.path.join(pawd, 'ei_conv_to_oac_ip', 'results_bhl_S1_2050_BL2_alt_sens_mach')

EICO2_SAF = 3.11

fig, ax = plt.subplots(1, 1)

metric_vec = ['ATR100', 'ATR20', 'EWAGWP100', 'EWAGWP20']

for metric in metric_vec:

    co2_metric_norm_mat = []
    total_co2_norm_mat = []
    total_fuel_burn_norm_mat = []

    co2_mean_factor_vec = []

    co2_metric_mat = []
    fuel_burn_fac_mat = []
    total_co2_mat = []
    total_fuel_burn_mat = []

    alt_feet_vec = []
    for FL in FL_vec:

        current_alt_feet = FL*100
        alt_feet_vec.append(current_alt_feet)
        current_spec_data_file = f"spec_data_FL{FL}_MR.xlsx"

        current_df = pd.read_excel(current_spec_data_file, sheet_name=metric)
        current_filtered_df = current_df[(current_df['einox_fac'] == 1) & (current_df['einvpm_fac'] == 0.00007)]
        current_co2_metric_vec = current_filtered_df['CO2'].values
        current_fuel_burn_fac_vec = current_filtered_df['fuel_burn_fac'].values

        co2_metric_mat.append(current_co2_metric_vec)
        fuel_burn_fac_mat.append(current_fuel_burn_fac_vec)

        current_baseline_results_file = os.path.join(baseline_alt_results_folder, f'Results_bhl_S1_2050_BL2_only_alt_{FL*100}.npz')
        data = np.load(current_baseline_results_file, allow_pickle=True)
        total_emission_grids = data['total_emission_grids']
        fuel_grid = total_emission_grids[0]
        total_grid_fuel = np.sum(fuel_grid)
        total_CO2 = (total_grid_fuel*EICO2_SAF)/(10**9)

        total_CO2_vec = [elem*total_CO2 for elem in fuel_burn_factor_range]
        total_co2_mat.append(total_CO2_vec)
        total_fuel_burn_vec = [float((elem*total_grid_fuel)/(10**9)) for elem in fuel_burn_factor_range]
        total_fuel_burn_mat.append(total_fuel_burn_vec)

        co2_metric_per_unit_fuel_vec = [float(elem1/(elem2*(10**3)*(10**9))) for elem1, elem2 in zip(current_co2_metric_vec, total_fuel_burn_vec)]
        co2_mean_factor_vec.append(np.mean(co2_metric_per_unit_fuel_vec))
        ax.scatter([(FL*100*0.3048)/1000]*len(co2_metric_per_unit_fuel_vec), co2_metric_per_unit_fuel_vec, color='k')

    print(metric, np.mean(co2_mean_factor_vec)/EICO2_SAF)
    fontsize=12.5
    ax.set_xlabel('Altitude [km]', fontsize=fontsize)
    ax.set_title('CO2', fontweight='bold')
    ax.set_ylabel('$ATR_{100,CO2}/fuel$ [K/kg fuel]', fontsize=fontsize)
    ax.tick_params(axis='both', labelsize=fontsize)
    #
    # ax2 = ax.twiny()
    # # ax2.set_xlim(0, 1)  # your own limits
    # ax2.set_xticks(alt_feet_vec)
    # # ax2.set_xticklabels([str(elem) for elem in alt_feet_vec])
    # ax2.set_xlabel('Second X axis')

    # plt.show()

