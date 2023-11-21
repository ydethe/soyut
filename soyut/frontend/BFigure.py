import typing as T

from .. import logger
from .BLayout import BGridSpec, BGridElement
from .GraphicSpec import AxeProjection
from .BAxe import ABaxe, BAxeFactory

__all__ = ["BFigure"]


class BFigure(object):
    def __init__(self, title: str) -> None:
        self.title = title
        self.grid_spec = None
        self.list_axes: T.List[ABaxe] = []

    def add_gridspec(self, nrows: int = 1, ncols: int = 1) -> BGridSpec:
        gs = BGridSpec(self, nrows=nrows, ncols=ncols)
        self.grid_spec = gs
        return gs

    def add_axe(
        self,
        title: str,
        spec: BGridElement,
        projection: AxeProjection = AxeProjection.RECTILINEAR,
        sharex: ABaxe = None,
        sharey: ABaxe = None,
        **kwargs,
    ) -> ABaxe:
        if spec.axe is None:
            """Creates a ABaxe"""
            axe = BAxeFactory.create(
                figure=self,
                title=title,
                spec=spec,
                projection=projection,
                sharex=sharex,
                sharey=sharey,
                kwargs=kwargs,
            )
            self.registerBAxe(axe)
            spec.axe = axe
        else:
            axe = spec.axe
            logger.debug("Reusing axe")

        return axe

    def registerBAxe(self, baxe: ABaxe):
        """Registers a new ABaxe in the list of related ABaxe

        Args:
            baxe: The ABaxe to add

        """
        self.list_axes.append(baxe)
