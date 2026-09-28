"""
Unit tests for preprocessing and coordinate extraction routines.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytest

from src.preprocess import find_nearest_indices


def test_find_nearest_indices_1d():
    lats = np.array([31.0, 32.5, 34.0, 35.5, 37.0])
    lons = np.array([73.0, 74.5, 76.0, 77.5, 79.0])
    
    # Target near Srinagar: lat 34.08, lon 74.80
    lat_idx, lon_idx, act_lat, act_lon = find_nearest_indices(lats, lons, 34.0837, 74.7973)
    assert lat_idx == 2  # 34.0 is closest to 34.0837
    assert lon_idx == 1  # 74.5 is closest to 74.7973
    assert np.isclose(act_lat, 34.0)
    assert np.isclose(act_lon, 74.5)


def test_find_nearest_indices_2d():
    lats_1d = np.array([32.0, 33.0, 34.0])
    lons_1d = np.array([74.0, 75.0, 76.0])
    lon_grid, lat_grid = np.meshgrid(lons_1d, lats_1d)

    lat_idx, lon_idx, act_lat, act_lon = find_nearest_indices(lat_grid, lon_grid, 33.1, 75.9)
    assert lat_idx == 1
    assert lon_idx == 2
    assert act_lat == 33.0
    assert act_lon == 76.0


def test_valid_time_calculation():
    init_time = datetime(2026, 9, 15, 0, 0, 0)
    forecast_hour = 48
    valid_time = init_time + timedelta(hours=forecast_hour)
    assert valid_time == datetime(2026, 9, 17, 0, 0, 0)


def test_kelvin_to_celsius_conversion():
    kelvin_temp = 293.15
    celsius_temp = kelvin_temp - 273.15
    assert np.isclose(celsius_temp, 20.0)


def test_physical_range_bounds():
    raw_temps = pd.Series([25.0, -10.0, -85.0, 65.0, 15.0])
    t_min, t_max = -40.0, 55.0
    valid_mask = (raw_temps >= t_min) & (raw_temps <= t_max)
    assert valid_mask.sum() == 3
    assert not valid_mask.iloc[2]  # -85.0 is out of bounds
    assert not valid_mask.iloc[3]  # 65.0 is out of bounds
