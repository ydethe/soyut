from abc import ABCMeta, abstractmethod, abstractproperty
import typing as T
from pathlib import Path

from networkx.classes.graph import Graph
import numpy as np
from numpy import pi
import pandas as pd

from .GPlottable import GPlottable
from ..utils import FloatArr
from .GraphicSpec import AxeProjection

if T.TYPE_CHECKING:
    from .BAxe import ABaxe
    from .BFigure import ABFigure
    from .GraphicSpec import FigureSpec
else:
    ABaxe = "blocksim.graphics.BAxe.ABaxe"
    ABFigure = "blocksim.graphics.BFigure.ABFigure"
    FigureSpec = "blocksim.graphics.GraphicSpec.FigureSpec"

__all__ = [
    "APlottable",
    "PlottableGraph",
    "PlottableGeneric",
    "APlottableDSPMap",
    "PlottableImage",
]


class APlottable(metaclass=ABCMeta):
    """This base abstract class describes all the entities able to be plotted:

    Daughter classes shall make sure that the class attribute *compatible_baxe* is up to date.

    * networkx graphs. See `PlottableGraph`
    * simple arrays. See `PlottableArray`
    * tuple of arrays or dictionaries, see `PlottableGeneric`. The dictionaries keys are:

        * data
        * name
        * unit

    Args:
        plottable: one of the instance above
        kwargs: The dictionary of options for plotting (color, width,etc)

    """

    __slots__ = ["name", "plottable", "kwargs", "twinx", "twiny"]

    def __init__(self, plottable, name: str, kwargs: dict) -> None:
        self.name = name
        self.plottable = plottable
        self.twinx = kwargs.pop("twinx", None)
        self.twiny = kwargs.pop("twiny", None)
        self.kwargs = kwargs

    @abstractmethod
    def _make_mline(self, axe: ABaxe) -> T.Tuple[FloatArr, FloatArr, str, str, str, str]:
        """This makes the job of turning a generic plottable into a tuple of useful values

        Returns:
            An numpy array of X coordinates
            An numpy array of Y coordinates
            The name of the X coordinate
            The physical unit of the X variable
            The name of the Y coordinate
            The physical unit of the Y variable

        """
        pass

    @abstractproperty
    def compatible_baxe(self) -> T.List[AxeProjection]:
        pass


class PlottableGraph(APlottable):
    """Allows plotting a networkx MultiDiGraph
    Only possible in `blocksim.graphics.GraphicSpec.FigureProjection.MPL`.
    Available plotting options:
    see https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html

    Args:
        plottable: a networkx MultiDiGraph instance
        kwargs: The dictionary of options for plotting (color, width,etc)

    """

    __slots__ = []

    @property
    def compatible_baxe(self) -> T.List[AxeProjection]:
        return [AxeProjection.GRAPH]


class PlottableGeneric(APlottable):

    __slots__ = []

    @property
    def compatible_baxe(self) -> T.List[AxeProjection]:
        return [
            AxeProjection.RECTILINEAR,
            AxeProjection.LOGX,
            AxeProjection.LOGY,
            AxeProjection.LOGXY,
            AxeProjection.NORTH_POLAR,
            AxeProjection.PLATECARREE,
            AxeProjection.POLAR,
        ]

    def _make_mline(self, axe: ABaxe) -> T.Tuple[FloatArr, FloatArr, str, str, str, str]:
        transform = self.kwargs.get("transform", lambda x: x)

        (
            xd,
            yd,
            name_of_x_var,
            unit_of_x_var,
            name_of_y_var,
            unit_of_y_var,
        ) = self.plottable.make_line(transform=transform)

        if axe.projection == AxeProjection.PLATECARREE:
            xd *= 180 / pi
            yd *= 180 / pi
            unit_of_x_var = "deg"
            unit_of_y_var = "deg"

        return xd, yd, name_of_x_var, unit_of_x_var, name_of_y_var, unit_of_y_var


class APlottableDSPMap(APlottable):
    """Specialisation of `APlottable` for `blocksim.dsp.DSPMap.ADSPMap`

    Args:
        plottable: a `blocksim.dsp.DSPMap.ADSPMap` instance
        kwargs: The dictionary of options for plotting (color, width,etc)

    """

    __slots__ = []


class PlottableImage(APlottableDSPMap):
    """Specialisation of `APlottable` for plotting images

    Args:
        plottable: a Path instance
        kwargs: The dictionary of options for plotting

    """

    __slots__ = []

    @property
    def compatible_baxe(self) -> T.List[AxeProjection]:
        return [
            AxeProjection.RECTILINEAR,
        ]

    def _make_mline(self, axe: ABaxe) -> T.Tuple[FloatArr, FloatArr, str, str, str, str]:
        pass


class PlottableFactory(object):
    """Factory class that instanciates the adapted daughter class
    of `APlottable` to handle the object to plot"""

    __slots__ = []

    @classmethod
    def create(cls, mline, name: str = "", kwargs: dict = {}) -> APlottable:
        """Creates the adapted daughter class of `APlottable` to handle the object to plot

        Args:
            mline: Object to plot. Can be:

            * a `blocksim.dsp.DSPLine.ADSPLine`
            * a `blocksim.dsp.DSPMap.ADSPMap`
            * a 2 elements tuple of numpy arrays
            * a simple numpy arrays
            * a networkx DiGraph
            * a 2 elements tuple of dictionaries, with keys:

                * data
                * name
                * unit

            name: Name of the plottable for identification
            kwargs: The plotting options for the object

        Returns:
            The APlottable instance suited to the object

        """
        if isinstance(mline, Graph):
            ret = PlottableGraph(mline, name, kwargs)

        elif isinstance(mline, tuple):
            if len(mline) == 0:
                raise AssertionError("Plottable reduced to an empty tuple")

            if np.isscalar(mline[0]):
                gp = GPlottable.from_serie(sy=mline)
            else:
                gp = GPlottable.from_tuple(mline)
            ret = PlottableGeneric(gp, name, kwargs)

        elif isinstance(mline, (pd.Series, np.ndarray, list)):
            gp = GPlottable.from_serie(sy=mline)
            ret = PlottableGeneric(gp, name, kwargs)

        elif isinstance(mline, GPlottable):
            if name == "" or name is None:
                name = mline.name
            gp = GPlottable.from_serie(sy=mline)
            ret = PlottableGeneric(gp, name, kwargs)

        elif isinstance(mline, Path):
            ret = PlottableImage(mline, name, kwargs)

        return ret
