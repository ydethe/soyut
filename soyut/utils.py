"""A set of useful functions

"""
import typing as T

import numpy as np
import numpy.typing as npt
from numpy import log10

if T.TYPE_CHECKING:
    from .frontend.BAxe import ABaxe
    from .frontend.BFigure import ABFigure
    from .frontend.GraphicSpec import FigureSpec
else:
    ABaxe = "soyut.frontend.BAxe.ABaxe"
    ABFigure = "soyut.frontend.BFigure.ABFigure"
    FigureSpec = "soyut.frontend.GraphicSpec.FigureSpec"

__all__ = ["ComplexArr", "FloatArr", "IntArr", "getUnitAbbrev", "format_parameter"]

ComplexArr = npt.NDArray[np.complex128]
FloatArr = npt.NDArray[np.float64]
IntArr = npt.NDArray[np.int64]


def getUnitAbbrev(
    samp: float, unit: str, force_mult: int = None
) -> T.Tuple[float, float, str, str]:
    """Given a scale factor, gives the prefix for the unit to display

    Args:
        samp: Sample
        unit: Physical unit
        force_mult: Multiplier to use

    Returns:
        scaled_samp: Scaled sample
        mult: Division coefficient of samp
        lbl: Scale factor label
        unit: Unit to display

    Example:
        >>> getUnitAbbrev(0.1, 's')
        (100.0, 0.001, 'm', 's')
        >>> getUnitAbbrev(13.6, 's')
        (13.6, 1, '', 's')
        >>> getUnitAbbrev(76, 's') # doctest: +ELLIPSIS
        (1.266..., 60, '', 'min')
        >>> getUnitAbbrev(1.5e-3, 'm')
        (1.5, 0.001, 'm', 'm')
        >>> getUnitAbbrev(1.5e-3, 's')
        (1.5, 0.001, 'm', 's')
        >>> getUnitAbbrev(90, 's')
        (1.5, 60, '', 'min')

    """
    d = {
        1: "",
        1000: "k",
        1e6: "M",
        1e9: "G",
        1e12: "T",
        1e-3: "m",
        1e-6: "µ",
        1e-9: "n",
        1e-12: "p",
        1e-15: "f",
        1e-18: "a",
        1e-21: "z",
        1e-24: "y",
    }
    d_time = {
        1: "s",
        60: "min",
        3600: "h",
        86400: "day",
        86400 * 30: "month",
        860400 * 30 * 12: "yr",
    }
    if unit == "s" and samp >= 1:
        if force_mult is None:
            for mult in reversed(d_time.keys()):
                if samp / mult >= 1:
                    break
        else:
            mult = force_mult
        unit = d_time[mult]
        lbl = ""
    else:
        if force_mult is None:
            if isinstance(samp, np.timedelta64):
                samp = np.timedelta64(samp, "s").astype(float)
            if samp == 0:
                samp = 1
            xm = np.abs(samp)
            pm = (int(np.ceil(log10(xm))) // 3) * 3
            mult = 10**pm
        else:
            mult = force_mult
        lbl = d[mult]

    if unit == "":
        unit = "-"

    return samp / mult, mult, lbl, unit


def format_parameter(
    samp: float, unit: str, unbreakable_space: bool = False
) -> T.Tuple[str, float]:
    """Given a scalar value and a unit, returns the txt to display
    with appropriate unit and muyliplier

    Args:
        samp: The scalar value
        unit: The associated unit

    Returns:

        * Text to display in the axis label
        * Division coefficient of samp

    Examples:
        >>> format_parameter(1.5e-3, 'm')
        '1.5 mm'
        >>> format_parameter(1.5e-3, 's')
        '1.5 ms'
        >>> format_parameter(90, 's')
        '1.5 min'

    """
    if unbreakable_space:
        space = "\u00A0"
    else:
        space = " "

    scaled_samp, mult, lbl, unit = getUnitAbbrev(samp, unit)
    txt = f"{scaled_samp:.3g}{space}{lbl}{unit}"
    return txt, mult
