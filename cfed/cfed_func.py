"""
date: 04/06/2026
time: 12:03
author: @hssaluja
"""

import numpy as np

CO2_ATR100_coeff = 3.762685118715418e-14
H2O_ATR100_coeff_vec = [3.00195615e-16, -7.37237732e-15, 6.10369069e-14, -1.69163426e-13]
# NOx_ATR100_coeff_vec = [1.45690965e-16, -2.01515805e-15, 8.18093102e-15, 1.28101580e-17, -5.04928969e-16, 1.09758374e-14]
CiC_ATR100_coeff_rich_burn_vec = [-2.57968053e-14, 5.70527213e-13, -2.76219979e-12, 1.927485704490916, 0.5779147450399053]
CiC_ATR100_coeff_lean_burn_vec = [1.40639100e-13, -3.11152978e-12, 1.50676877e-11, -2.25957837e-14, 4.98946195e-13, -2.41315195e-12]

lean_vs_rich_einvpm_threshold = 1E14
reference_einvpm = 1.5E15

def cfed_func(EICO2, EIH2O, EINOx_cruise, EInvPM_num_cruise, altitude_km, metric):
    """
        Calculates the climate response in ATR100 per unit fuel for CO2, NOx, H2O and ATR100 per unit distance
        traversed for Contrail-induced cirrus (CiC) for given values of relevant emission indices and cruise altitude

        Args:
            EICO2 (float): Emission index of CO2 [kg kg(fuel)^-1]
            EIH2O (float): Emission index of H2O [kg kg(fuel)^-1]
            EINOx_cruise (float): Emission index of NOx [g kg(fuel)^-1]
            EInvPM_num_cruise (float): Number Emission index of nvPM [# kg(fuel)^-1]
            altitude_km (float): Altitude [km]
            metric (string): Climate metric type (currently supports only ATR100).

        Returns:
            CO2_metric_per_unit_fuel_burn (float): CO2 ATR100 per unit fuel [K kg(fuel)^-1]
            H2O_metric_per_unit_fuel_burn (float): H2O ATR100 per unit fuel [K kg(fuel)^-1]
            NOx_metric_per_unit_fuel_burn (float): NOx ATR100 per unit fuel [K kg(fuel)^-1]
            CiC_metric_per_unit_flown_km (float): CiC ATR100 per unit distance traversed [K (km)^-1]

    """

    if metric == 'ATR100':
        CO2_coeff = CO2_ATR100_coeff
        H2O_coeff_a0, H2O_coeff_a1, H2O_coeff_a2, H2O_coeff_a3 = H2O_ATR100_coeff_vec
        NOx_coeff_a0, NOx_coeff_a1, NOx_coeff_a2, NOx_coeff_b0, NOx_coeff_b1, NOx_coeff_b2 = NOx_ATR100_coeff_vec
        CiC_coeff_rich_burn_a0, CiC_coeff_rich_burn_a1, CiC_coeff_rich_burn_a2, CiC_coeff_rich_burn_b, CiC_coeff_rich_burn_c = CiC_ATR100_coeff_rich_burn_vec
        CiC_coeff_lean_burn_a0, CiC_coeff_lean_burn_a1, CiC_coeff_lean_burn_a2, CiC_coeff_lean_burn_b0, CiC_coeff_lean_burn_b1, CiC_coeff_lean_burn_b2 = CiC_ATR100_coeff_lean_burn_vec
    else:
        raise ValueError('Metric not recognized.')

    CO2_metric_per_unit_fuel_burn = CO2_coeff * EICO2

    H2O_metric_per_unit_fuel_burn = ((H2O_coeff_a0*(altitude_km**3)) + (H2O_coeff_a1*(altitude_km**2)) + (H2O_coeff_a2*altitude_km) + H2O_coeff_a3)*EIH2O

    NOx_metric_per_unit_fuel_burn = EINOx_cruise*((NOx_coeff_a0 * (altitude_km ** 2)) + (NOx_coeff_a1 * (altitude_km)) + NOx_coeff_a2) + ((NOx_coeff_b0 * (altitude_km ** 2)) + (NOx_coeff_b1 * (altitude_km)) + NOx_coeff_b2)

    comb_mode = None
    CiC_metric_per_unit_flown_km = None
    if EInvPM_num_cruise >= lean_vs_rich_einvpm_threshold:
        comb_mode = 'Rich'
        CiC_metric_per_unit_flown_km = ((CiC_coeff_rich_burn_a0 * (altitude_km**2)) + (CiC_coeff_rich_burn_a1 * altitude_km) + CiC_coeff_rich_burn_a2) * (np.arctan(CiC_coeff_rich_burn_b * ((EInvPM_num_cruise/reference_einvpm)**CiC_coeff_rich_burn_c)))

    elif EInvPM_num_cruise < lean_vs_rich_einvpm_threshold:
        comb_mode = 'Lean'
        CiC_metric_per_unit_flown_km = (((CiC_coeff_lean_burn_a0 * (altitude_km**2)) + (CiC_coeff_lean_burn_a1 * (altitude_km)) + (CiC_coeff_lean_burn_a2)) * (EInvPM_num_cruise/reference_einvpm)) + ((CiC_coeff_lean_burn_b0 * (altitude_km**2)) + (CiC_coeff_lean_burn_b1 * (altitude_km)) + (CiC_coeff_lean_burn_b2))

    return CO2_metric_per_unit_fuel_burn, H2O_metric_per_unit_fuel_burn, NOx_metric_per_unit_fuel_burn, CiC_metric_per_unit_flown_km