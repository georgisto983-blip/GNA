"""RDDS (Recoil Distance Doppler Shift) half-life calculations.

Physical basis
--------------
After Coulomb excitation or a fusion-evaporation reaction, recoiling nuclei
travel from the target toward a stopper foil at velocity beta*c.  Gamma rays
emitted in flight are Doppler-shifted; those emitted after the nucleus has
been stopped in the foil are not.

For a nuclear state with mean lifetime tau:

    R  =  I_u / (I_u + I_s)  =  exp( -d / (beta * c * tau) )

where
    I_u   = area of the unshifted (stopped) gamma-ray peak
    I_s   = area of the Doppler-shifted (in-flight) peak
    d     = target-to-stopper distance
    beta  = recoil velocity in units of c
    c     = speed of light

Single distance
    tau     = -d / (beta * c * ln(R))
    T_{1/2} = tau * ln(2)

Multiple distances
    Plot ln(R) vs d and perform a linear fit.  The slope m satisfies
        m = -1e-6 / (beta * c * tau)     (d in micrometers)
    so
        T_{1/2} = ln(2) * 1e-6 / (beta * c * |m|)

Assumptions & limitations
    * Feeding from higher-lying states is assumed to be negligible.
      When feeding is significant a full Differential Decay Curve Method
      (DDCM) analysis should be used instead.
    * ODR (Orthogonal Distance Regression) is used for the multi-distance
      fit because both the distance and ln(R) carry experimental
      uncertainties.
"""

import math
import numpy as np
from uncertainties import ufloat, UFloat
from uncertainties.umath import log as ulog
from scipy.odr import ODR, Model, RealData

C_LIGHT = 299_792_458  # m/s  (exact, SI definition)


def _log(x):
    """Natural logarithm that handles both float and UFloat."""
    return ulog(x) if isinstance(x, UFloat) else math.log(x)


def halflife_single(distance_um, beta, area_shifted, area_unshifted):
    """Half-life from a single plunger distance measurement.

    Parameters
    ----------
    distance_um : float or UFloat
        Target–stopper distance in micro-meters.
    beta : float or UFloat
        Recoil velocity v/c.
    area_shifted : float or UFloat
        Area of the Doppler-shifted peak.
    area_unshifted : float or UFloat
        Area of the unshifted (stopped) peak.

    Returns
    -------
    float or UFloat
        Half-life in seconds.

    Raises
    ------
    ValueError
        If the intensity ratio is outside the physical range (0, 1).
    """
    total = area_unshifted + area_shifted
    R = area_unshifted / total

    R_nom = R.nominal_value if isinstance(R, UFloat) else R
    if R_nom <= 0 or R_nom >= 1:
        raise ValueError(
            f"Intensity ratio R = I_u/(I_u+I_s) = {R_nom:.4f} is outside "
            "the physical range (0, 1).\n"
            "Check that both peak areas are positive and that I_s > 0."
        )

    d_m = distance_um * 1e-6  # um -> m
    tau = -d_m / (beta * C_LIGHT * _log(R))
    return tau * math.log(2)


def halflife_multi(distances, areas_shifted, areas_unshifted, beta):
    """Half-life from multiple distances via ODR linear fit of ln(R) vs d.

    Parameters
    ----------
    distances : list of ufloat
        Plunger distances in micro-meters.
    areas_shifted : list of ufloat
        Shifted peak areas.
    areas_unshifted : list of ufloat
        Unshifted peak areas.
    beta : ufloat
        Recoil velocity v/c.

    Returns
    -------
    t_half : UFloat
        Half-life in seconds.
    odr_output : scipy.odr.Output
        Full ODR regression result (contains slope, intercept, etc.).
    x, x_err, y, y_err : ndarray
        Numerical arrays used for the fit (useful for plotting).
    """
    log_ratios = [
        ulog(u / (u + s))
        for u, s in zip(areas_unshifted, areas_shifted)
    ]

    x = np.array([d.nominal_value for d in distances])
    x_err = np.array([d.std_dev for d in distances])
    y = np.array([lr.nominal_value for lr in log_ratios])
    y_err = np.array([lr.std_dev for lr in log_ratios])

    def linear(p, x):
        return p[0] * x + p[1]

    model = Model(linear)
    data = RealData(x, y, sx=x_err, sy=y_err)
    odr = ODR(data, model, beta0=[-0.1, 0.0])
    result = odr.run()

    slope = ufloat(result.beta[0], result.sd_beta[0])
    t_half = math.log(2) * 1e-6 / (beta * abs(slope) * C_LIGHT)

    return t_half, result, x, x_err, y, y_err
