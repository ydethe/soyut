import typing as T

from abc import ABCMeta, abstractproperty

import numpy as np
from numpy import pi, sqrt, cos, sin

from ..constants import Req
from .GraphicSpec import AxeProjection
from .BLayout import BGridElement
from .Plottable import (
    APlottable,
    PlottableFactory,
)

if T.TYPE_CHECKING:
    from .BFigure import ABFigure
    from .GraphicSpec import FigureSpec
else:
    ABFigure = "soyut.frontend.BFigure.ABFigure"
    FigureSpec = "soyut.frontend.GraphicSpec.FigureSpec"


class ABaxe(metaclass=ABCMeta):
    """Class that describes the axe. Not yet a matplotlib axe

    Args:
        figure: Parent figure containing the BAxe
        title: Title of the axe
        spec: Position in the BGridSpec
        sharex: ABaxe instance to share X limits with
        sharey: ABaxe instance to share Y limits with

    """

    __slots__ = [
        "figure",
        "title",
        "spec",
        "parent_sharex",
        "children_sharex",
        "parent_sharey",
        "children_sharey",
        "kwargs",
        "list_plottables",
        "xbounds",
        "ybounds",
    ]

    def __init__(
        self,
        figure: ABFigure,
        title: str,
        spec: BGridElement,
        sharex: "ABaxe" = None,
        sharey: "ABaxe" = None,
        kwargs={},
    ):
        self.figure: ABFigure = figure
        self.title: str = title
        self.spec: BGridElement = spec
        self.parent_sharex: "ABaxe" = sharex
        self.children_sharex: T.List["ABaxe"] = []
        self.parent_sharey: "ABaxe" = sharey
        self.children_sharey: T.List["ABaxe"] = []
        self.kwargs: dict = kwargs

        if sharex is None:
            self.xbounds = None, None
        else:
            self.xbounds = sharex.xbounds
            sharex._addChildSharex(self)

        if sharey is None:
            self.ybounds = None, None
        else:
            self.ybounds = sharey.xbounds
            sharey._addChildSharey(self)

        self.list_plottables = []

    @abstractproperty
    def projection(self) -> AxeProjection:
        pass

    def _addChildSharex(self, sharex: "ABaxe"):
        self.children_sharex.append(sharex)

    def _addChildSharey(self, sharey: "ABaxe"):
        self.children_sharey.append(sharey)

    def _findRootSharex(self) -> "ABaxe":
        if self.parent_sharex is None:
            return self
        else:
            return self.parent_sharex._findRootSharex()

    def _findRootSharey(self) -> "ABaxe":
        if self.parent_sharey is None:
            return self
        else:
            return self.parent_sharey._findRootSharey()

    def registerPlottable(self, plottable: APlottable):
        """Registers the APlottable in the list of objects handled by the axe

        Args:
            plottable: APlottable object

        """

        if self.projection not in plottable.compatible_baxe:
            raise AssertionError(f"{self.projection} not in {plottable.compatible_baxe}")

        self.list_plottables.append(plottable)

    def set_xlim(self, xmin: float = None, xmax: float = None, _from_root: bool = True):
        """Set X limits
        The values are given in S.I. units (without scaling)

        Args:
            xmin: The left xlim in data coordinates. Passing None leaves the limit unchanged.
            xmax: The right xlim in data coordinates. Passing None leaves the limit unchanged.

        """
        if _from_root:
            rootx = self._findRootSharex()
        else:
            rootx = self

        rootx.xbounds = xmin, xmax
        for axe in rootx.children_sharex:
            axe.set_xlim(xmin, xmax, _from_root=False)

    def set_ylim(self, ymin: float = None, ymax: float = None, _from_root: bool = True):
        """Set Y limits
        The values are given in S.I. units (without scaling)

        Args:
            ymin: The left ylim in data coordinates. Passing None leaves the limit unchanged.
            ymax: The right ylim in data coordinates. Passing None leaves the limit unchanged.

        """
        if _from_root:
            rooty = self._findRootSharey()
        else:
            rooty = self

        rooty.ybounds = ymin, ymax
        for axe in rooty.children_sharey:
            axe.set_ylim(ymin, ymax, _from_root=False)

    def plot(self, plottable, **kwargs) -> APlottable:
        """Records the plot command (without executing it) and does some checks

        Args:
            plottable: Object to plot. Can be:

            * a `blocksim.dsp.DSPLine.ADSPLine`
            * a `blocksim.dsp.DSPMap.ADSPMap`
            * a 2 elements tuple of numpy arrays
            * a simple numpy arrays
            kwargs: The plotting options for the object

        """
        if plottable is None:
            return
        name = kwargs.pop("name", "")
        res = PlottableFactory.create(plottable, name=name, kwargs=kwargs)
        self.registerPlottable(res)
        return res

    def scatter(self, plottable, **kwargs) -> APlottable:
        """Records the scatter command (without executing it) and does some checks

        Args:
            plottable: Object to plot. Can be:

            * a `blocksim.dsp.DSPLine.ADSPLine`
            * a `blocksim.dsp.DSPMap.ADSPMap`
            * a 2 elements tuple of numpy arrays
            * a simple numpy arrays
            kwargs: The plotting options for the object

        """
        if plottable is None:
            return
        if "marker" not in kwargs:
            kwargs["marker"] = "+"
        kwargs["linestyle"] = ""
        return self.plot(plottable=plottable, **kwargs)


class BAxeGraph(ABaxe):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.GRAPH


class BAxeRectilinear(ABaxe):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.RECTILINEAR


class BAxeSemiLogX(BAxeRectilinear):

    __slots__ = []

    def projection(self) -> AxeProjection:
        return AxeProjection.LOGX


class BAxeSemiLogY(BAxeRectilinear):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.LOGY


class BAxeSemiLogXY(BAxeRectilinear):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.LOGXY


class BAxePolar(ABaxe):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.POLAR


class BAxeNorthPolar(ABaxe):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.NORTH_POLAR


class BAxePlateCarree(ABaxe):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.PLATECARREE

    def plotDeviceReach(
        self, coord: tuple, elev_min: float, sat_alt: float, **kwargs
    ) -> APlottable:
        """Plots a line that represents the device reach

        See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
        for the possible values in kwargs

        Args:
            coord: The position of the point, in longitude/latitude (rad)
            elev_min: Minimum elevation angle (rad)
            sat_alt: Satellite altitude, **assuming circular orbit** (m)
            kwargs: The plotting options for the object

        Returns:
            The created APlottable

        """
        from cartopy.geodesic import Geodesic

        g_lon, g_lat = coord

        # https://scitools.org.uk/cartopy/docs/v0.17/cartopy/geodesic.html#cartopy.geodesic.Geodesic.circle
        r = Req + sat_alt
        d_lim = sqrt(r**2 - Req**2 * cos(elev_min) ** 2) - Req * sin(elev_min)
        alpha_lim = np.arccos((Req**2 + r**2 - d_lim**2) / (2 * r * Req))
        rad = alpha_lim * Req

        g = Geodesic()
        val = g.circle(g_lon * 180 / pi, g_lat * 180 / pi, radius=rad)
        c_lon = np.array(val[:, 0])
        c_lat = np.array(val[:, 1])

        return self.plot(plottable=(c_lon * pi / 180, c_lat * pi / 180), **kwargs)


class BAxeDim3D(ABaxe):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.DIM3D


class BAxePanda3D(ABaxe):

    __slots__ = []

    @property
    def projection(self) -> AxeProjection:
        return AxeProjection.PANDA3D


class BAxeFactory(object):
    """Factory class that instanciates the adapted daughter class
    of `APlottable` to handle the object to plot"""

    __slots__ = []

    @classmethod
    def create(
        cls,
        figure: ABFigure,
        title: str,
        spec: BGridElement,
        projection: AxeProjection,
        sharex: ABaxe = None,
        sharey: ABaxe = None,
        kwargs={},
    ) -> ABaxe:
        """Creates the adapted daughter class of `ABaxe`

        Args:
            figure: parent BFigure
            title: title of the BAxe
            spec : coordinates of the BAxe in the BFigure's layout
            projection: projection of the BAxe. Used to determine which subclass of ABaxe to use
            sharex: ABaxe to share X limits with
            sharey: ABaxe to share Y limits with
            kwargs: The plotting options for the object

        Returns:
            The ABaxe instance suited to the projection

        """

        if projection == AxeProjection.DIM3D:
            baxe = BAxeDim3D(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.NORTH_POLAR:
            baxe = BAxeNorthPolar(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.PLATECARREE:
            baxe = BAxePlateCarree(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.POLAR:
            baxe = BAxePolar(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.RECTILINEAR:
            baxe = BAxeRectilinear(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.LOGX:
            baxe = BAxeSemiLogX(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.LOGY:
            baxe = BAxeSemiLogY(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.LOGXY:
            baxe = BAxeSemiLogXY(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.GRAPH:
            baxe = BAxeGraph(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )
        elif projection == AxeProjection.PANDA3D:
            baxe = BAxePanda3D(
                figure,
                title,
                spec,
                sharex,
                sharey,
                kwargs,
            )

        return baxe
