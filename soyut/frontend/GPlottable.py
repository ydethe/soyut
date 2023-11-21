import typing as T
from dataclasses import dataclass
from datetime import timedelta

from numpy.polynomial import Polynomial
import numpy as np
import pandas as pd
from pandas import DataFrame, Timestamp

from .. import logger

if T.TYPE_CHECKING:
    from .GPlottable import GPlottable
    from .GPlottable import GVariable
else:
    GPlottable = "blocksim.graphics.GPlottable.GPlottable"
    GVariable = "blocksim.graphics.GPlottable.GVariable"


class GVariable(object):
    """Generic plottable"""

    __slots__ = ["name", "data", "unit", "path"]

    def __init__(self, data: list = [], name: str = "", unit: str = "-", path: str = ""):
        self.data = data
        self.name = name
        self.unit = unit
        self.path = path

    @classmethod
    def from_desc(cls, desc) -> "GVariable":
        if isinstance(desc, dict):
            ret = GVariable.from_dict(desc)
        elif isinstance(desc, (np.ndarray, pd.Series, tuple, list)):
            ret = GVariable.from_serie(desc)
        else:
            logger.error(f"Don't know how to build GVariable from type '{type(desc)}'")
            raise TypeError(f"{type(desc)}")

        return ret

    @classmethod
    def from_serie(cls, s: pd.Series) -> "GVariable":
        ret = cls()
        ret.data = np.array(s)
        ret.name = ""
        ret.unit = "-"
        ret.path = ""

        return ret

    @classmethod
    def from_dict(cls, d: dict) -> "GVariable":
        ret = cls()
        ret.data = d.get("data", np.array([]))
        ret.name = d.get("name", "")
        ret.unit = d.get("unit", "-")
        ret.path = d.get("path", "")

        return ret

    @classmethod
    def from_dataframe(cls, df: DataFrame, name: str) -> "GVariable":
        ret = cls()
        ret.data = np.array(df[name])
        ret.name = name
        ret.unit = "-"
        ret.path = "/" + name

        return ret

    def detrend(self, deg: int = 1) -> GVariable:
        y = self.data
        ns = len(y)
        x = np.arange(ns)

        p = Polynomial.fit(x, y, deg=deg)
        ret = np.array(y) - p(x)

        rdesc = GVariable(data=ret, name=self.name + " (detrended)", unit=self.unit, path=self.path)

        return rdesc

    def __add__(self, y: GVariable) -> GVariable:
        rdesc = GVariable(
            data=np.array(self.data) + np.array(y.data),
            name=self.name,
            unit=self.unit,
            path=self.path,
        )

        return rdesc

    def __neg__(self) -> GVariable:
        rdesc = GVariable(data=-np.array(self.data), name=self.name, unit=self.unit, path=self.path)

        return rdesc

    def __sub__(self, y: GVariable) -> GVariable:
        my = -y
        return self + my

    def __mul__(self, y: GVariable) -> GVariable:
        rdesc = GVariable(
            data=np.array(self.data) * np.array(y.data),
            name=self.name,
            unit=self.unit,
            path=self.path,
        )

        return rdesc

    def __div__(self, y: GVariable) -> GVariable:
        rdesc = GVariable(
            data=np.array(self.data) / np.array(y.data),
            name=self.name,
            unit=self.unit,
            path=self.path,
        )

        return rdesc


@dataclass(init=True)
class GPlottable:
    name: str
    xvar: GVariable
    yvar: GVariable

    def detrend(self, deg: int = 1) -> GPlottable:
        rdesc = self.yvar.detrend(deg=deg)

        return GPlottable(xvar=self.xvar, yvar=rdesc)

    @classmethod
    def from_serie(cls, sy: pd.Series, sx: pd.Series = None, name: str = "") -> "GPlottable":
        yvar = GVariable.from_serie(sy)

        if sx is None:
            ns = len(yvar.data)
            xvar = GVariable(data=np.arange(ns))
        else:
            xvar = GVariable.from_serie(sx)

        ret = cls(xvar=xvar, yvar=yvar, name=name)

        return ret

    @classmethod
    def from_dict(cls, dy: dict, dx: dict = None, name: str = "") -> "GPlottable":
        yvar = GVariable.from_dict(dy)

        if dx is None:
            ns = len(yvar.data)
            xvar = GVariable(data=np.arange(ns))
        else:
            xvar = GVariable.from_dict(dx)

        ret = cls(xvar=xvar, yvar=yvar, name=name)

        return ret

    @classmethod
    def from_dataframe(cls, df: DataFrame, yname: str, xname: str) -> "GPlottable":
        yvar = GVariable.from_dataframe(df, yname)

        if xname is None or xname == "":
            ns = len(yvar.data)
            xvar = GVariable(data=np.arange(ns))
        else:
            xvar = GVariable.from_dataframe(df, xname)

        ret = cls(xvar=xvar, yvar=yvar, name=yname)

        return ret

    @classmethod
    def from_tuple(cls, mline: tuple, name: str = "") -> "GPlottable":
        if len(mline) == 3:
            if isinstance(mline[0], pd.DataFrame):
                df, xdesc, ydesc = mline
                ret = cls.from_dataframe(df, ydesc, xdesc)

        elif len(mline) == 2:
            xdesc, ydesc = mline
            xvar = GVariable.from_desc(xdesc)
            yvar = GVariable.from_desc(ydesc)
            ret = cls(xvar=xvar, yvar=yvar, name=name)

        return ret

    def make_line(self, transform: T.Callable = lambda x: x):
        xd = self.xvar.data
        yd = self.yvar.data

        if isinstance(xd[0], (np.timedelta64, timedelta, Timestamp)):
            s = pd.Series(data=xd)
            xd = np.array(s).astype("timedelta64[s]").astype(np.float64)

        if isinstance(yd[0], (np.timedelta64, timedelta, Timestamp)):
            s = pd.Series(data=yd)
            yd = np.array(s).astype("timedelta64[s]").astype(np.float64)

        yd = transform(yd)

        name_of_x_var = self.xvar.name
        unit_of_x_var = self.xvar.unit
        name_of_y_var = self.yvar.name
        unit_of_y_var = self.yvar.unit

        if unit_of_x_var == "":
            unit_of_x_var = "-"

        if unit_of_y_var == "":
            unit_of_y_var = "-"

        return xd, yd, name_of_x_var, unit_of_x_var, name_of_y_var, unit_of_y_var


if __name__ == "__main__":
    a = GVariable(data=[1, 2])
    b = GVariable(data=[1, 2])
    print(b - a)
