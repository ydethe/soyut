import typing as T

if T.TYPE_CHECKING:
    from .BLayout import BGridSpec
    from .BFigure import BFigure
else:
    BGridSpec = "soyut.frontend.BLayout.BGridSpec"
    BFigure = "soyut.frontend.BFigure.BFigure"


class BGridElement(object):
    """This class stores the position of an axe in a grid

    Args:
        gs: Grid that gives axes' positions in a BFigure
        coord: Position of the BGridElement in the grid

    """

    __slots__ = ["axe", "gs", "coord"]

    def __init__(self, gs: BGridSpec, coord: slice):
        self.axe = None
        self.gs = gs
        self.coord: T.Tuple[slice, slice] = coord

    def get_gridspec(self) -> BGridSpec:
        """Returns the BGridSpec associated with the BGridElement

        Returns:
            The BGridSpec associated with the BGridElement

        """
        return self.gs

    def getFigure(self) -> BFigure:
        return self.gs.figure


class BGridSpec(object):
    """This class stores the layout of the axes in a BFigure

    Args:
        figure: Refering BFigure
        nrows: Number of rows of the layout
        ncols: Number of columns of the layout

    """

    __slots__ = ["figure", "nrows", "ncols"]

    def __init__(self, figure: BFigure, nrows: int, ncols: int):
        self.figure: BFigure = figure
        self.nrows: int = nrows
        self.ncols: int = ncols

    def __getitem__(self, ind) -> BGridElement:
        ge = BGridElement(gs=self, coord=ind)
        return ge
