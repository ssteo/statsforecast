# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/src/utils.ipynb.

# %% auto 0
__all__ = ['AirPassengers', 'AirPassengersDF', 'generate_series']

# %% ../nbs/src/utils.ipynb 3
import os
import warnings

import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import norm

from utilsforecast.compat import DataFrame
from utilsforecast.data import generate_series as utils_generate_series

# %% ../nbs/src/utils.ipynb 4
# Global variables
NOGIL = bool(os.getenv("NIXTLA_NUMBA_RELEASE_GIL", ""))
LEGACY_CACHE = bool(os.getenv("NUMBA_CACHE", ""))
if LEGACY_CACHE:
    warnings.warn(
        "The NUMBA_CACHE environment variable has been renamed to NIXTLA_NUMBA_CACHE. "
        "Please set that one instead.",
        FutureWarning,
    )
CACHE = bool(os.getenv("NIXTLA_NUMBA_CACHE", "")) or LEGACY_CACHE

# %% ../nbs/src/utils.ipynb 7
def generate_series(
    n_series: int,
    freq: str = "D",
    min_length: int = 50,
    max_length: int = 500,
    n_static_features: int = 0,
    equal_ends: bool = False,
    engine: str = "pandas",
    seed: int = 0,
) -> DataFrame:
    """Generate Synthetic Panel Series.

    Generates `n_series` of frequency `freq` of different lengths in the interval [`min_length`, `max_length`].
    If `n_static_features > 0`, then each series gets static features with random values.
    If `equal_ends == True` then all series end at the same date.

    Parameters
    ----------
    n_series : int
        Number of series for synthetic panel.
    freq : str (default='D')
        Frequency of the data, 'D' or 'M'.
    min_length : int (default=50)
        Minimum length of synthetic panel's series.
    max_length : int (default=500)
        Maximum length of synthetic panel's series.
    n_static_features : int (default=0)
        Number of static exogenous variables for synthetic panel's series.
    equal_ends : bool (default=False)
        Series should end in the same date stamp `ds`.
    engine : str (default='pandas')
        Output Dataframe type ('pandas' or 'polars').
    seed : int (default=0)
        Random seed used for generating the data.

    Returns
    -------
    pandas or polars DataFrame
        Synthetic panel with columns [`unique_id`, `ds`, `y`] and exogenous.
    """
    return utils_generate_series(
        n_series=n_series,
        freq=freq,
        min_length=min_length,
        max_length=max_length,
        n_static_features=n_static_features,
        equal_ends=equal_ends,
        engine=engine,
        seed=seed,
    )

# %% ../nbs/src/utils.ipynb 11
AirPassengers = np.array(
    [
        112.0,
        118.0,
        132.0,
        129.0,
        121.0,
        135.0,
        148.0,
        148.0,
        136.0,
        119.0,
        104.0,
        118.0,
        115.0,
        126.0,
        141.0,
        135.0,
        125.0,
        149.0,
        170.0,
        170.0,
        158.0,
        133.0,
        114.0,
        140.0,
        145.0,
        150.0,
        178.0,
        163.0,
        172.0,
        178.0,
        199.0,
        199.0,
        184.0,
        162.0,
        146.0,
        166.0,
        171.0,
        180.0,
        193.0,
        181.0,
        183.0,
        218.0,
        230.0,
        242.0,
        209.0,
        191.0,
        172.0,
        194.0,
        196.0,
        196.0,
        236.0,
        235.0,
        229.0,
        243.0,
        264.0,
        272.0,
        237.0,
        211.0,
        180.0,
        201.0,
        204.0,
        188.0,
        235.0,
        227.0,
        234.0,
        264.0,
        302.0,
        293.0,
        259.0,
        229.0,
        203.0,
        229.0,
        242.0,
        233.0,
        267.0,
        269.0,
        270.0,
        315.0,
        364.0,
        347.0,
        312.0,
        274.0,
        237.0,
        278.0,
        284.0,
        277.0,
        317.0,
        313.0,
        318.0,
        374.0,
        413.0,
        405.0,
        355.0,
        306.0,
        271.0,
        306.0,
        315.0,
        301.0,
        356.0,
        348.0,
        355.0,
        422.0,
        465.0,
        467.0,
        404.0,
        347.0,
        305.0,
        336.0,
        340.0,
        318.0,
        362.0,
        348.0,
        363.0,
        435.0,
        491.0,
        505.0,
        404.0,
        359.0,
        310.0,
        337.0,
        360.0,
        342.0,
        406.0,
        396.0,
        420.0,
        472.0,
        548.0,
        559.0,
        463.0,
        407.0,
        362.0,
        405.0,
        417.0,
        391.0,
        419.0,
        461.0,
        472.0,
        535.0,
        622.0,
        606.0,
        508.0,
        461.0,
        390.0,
        432.0,
    ]
)

# %% ../nbs/src/utils.ipynb 12
AirPassengersDF = pd.DataFrame(
    {
        "unique_id": np.ones(len(AirPassengers)),
        "ds": pd.date_range(start="1949-01-01", periods=len(AirPassengers), freq="M"),
        "y": AirPassengers,
    }
)

# %% ../nbs/src/utils.ipynb 17
@njit(nogil=NOGIL, cache=CACHE)
def _repeat_val_seas(season_vals: np.ndarray, h: int, season_length: int):
    out = np.empty(h, np.float32)
    for i in range(h):
        out[i] = season_vals[i % season_length]
    return out


@njit(nogil=NOGIL, cache=CACHE)
def _seasonal_naive(
    y: np.ndarray,  # time series
    h: int,  # forecasting horizon
    fitted: bool,  # fitted values
    season_length: int,  # season length
):
    if y.size < season_length:
        return {"mean": np.full(h, np.nan, np.float32)}
    n = y.size
    season_vals = np.empty(season_length, np.float32)
    fitted_vals = np.full(y.size, np.nan, np.float32)
    for i in range(season_length):
        s_naive = _naive(
            y[(i + n % season_length) :: season_length], h=1, fitted=fitted
        )
        season_vals[i] = s_naive["mean"].item()
        if fitted:
            fitted_vals[(i + n % season_length) :: season_length] = s_naive["fitted"]
    out = _repeat_val_seas(season_vals=season_vals, h=h, season_length=season_length)
    fcst = {"mean": out}
    if fitted:
        fcst["fitted"] = fitted_vals[-n:]
    return fcst


@njit(nogil=NOGIL, cache=CACHE)
def _repeat_val(val: float, h: int):
    return np.full(h, val, np.float32)


@njit(nogil=NOGIL, cache=CACHE)
def _naive(
    y: np.ndarray,  # time series
    h: int,  # forecasting horizon
    fitted: bool,  # fitted values
):
    mean = _repeat_val(val=y[-1], h=h)
    if fitted:
        fitted_vals = np.full(y.size, np.nan, np.float32)
        fitted_vals[1:] = np.roll(y, 1)[1:]
        return {"mean": mean, "fitted": fitted_vals}
    return {"mean": mean}

# %% ../nbs/src/utils.ipynb 19
# Functions used for calculating prediction intervals
def _quantiles(level):
    level = np.asarray(level)
    z = norm.ppf(0.5 + level / 200)
    return z


def _calculate_intervals(out, level, h, sigmah):
    z = _quantiles(np.asarray(level))
    zz = np.repeat(z, h)
    zz = zz.reshape(z.shape[0], h)
    lower = out["mean"] - zz * sigmah
    upper = out["mean"] + zz * sigmah
    pred_int = {
        **{f"lo-{lv}": lower[i] for i, lv in enumerate(level)},
        **{f"hi-{lv}": upper[i] for i, lv in enumerate(level)},
    }
    return pred_int


def _calculate_sigma(residuals, n):
    if n > 0:
        sigma = np.nansum(residuals**2)
        sigma = sigma / n
        sigma = np.sqrt(sigma)
    else:
        sigma = 0
    return sigma

# %% ../nbs/src/utils.ipynb 20
class ConformalIntervals:
    """Class for storing conformal intervals metadata information."""

    def __init__(
        self,
        n_windows: int = 2,
        h: int = 1,
        method: str = "conformal_distribution",
    ):
        if n_windows < 2:
            raise ValueError(
                "You need at least two windows to compute conformal intervals"
            )
        allowed_methods = ["conformal_distribution"]
        if method not in allowed_methods:
            raise ValueError(f"method must be one of {allowed_methods}")
        self.n_windows = n_windows
        self.h = h
        self.method = method
