import typing as T

import numpy as np
from matplotlib.figure import Figure as MFigure
import plotly.graph_objects as go

from soyut.frontend.BAxe import ABaxe
from soyut.frontend.BFigure import BFigure
from soyut.frontend.BLayout import BGridSpec


def simple_mpl_renderer(fig: BFigure) -> MFigure:
    from matplotlib import pyplot as plt

    mfig = plt.figure()
    mfig.suptitle(fig.title)
    mgs = mfig.add_gridspec(nrows=fig.grid_spec.nrows, ncols=fig.grid_spec.ncols)

    for axe in fig.list_axes:
        mge = mgs[axe.spec.coord]
        maxe = mfig.add_subplot(mge)
        maxe.set_title(axe.title)
        maxe.grid(True)

        for plottable in axe.list_plottables:
            (
                xd,
                yd,
                name_of_x_var,
                unit_of_x_var,
                name_of_y_var,
                unit_of_y_var,
            ) = plottable._make_mline(axe)

            maxe.plot(xd, yd)
            maxe.set_xlabel(f"{name_of_x_var} ({unit_of_x_var})")
            maxe.set_ylabel(f"{name_of_y_var} ({unit_of_y_var})")

    plt.show()


def get_axe_coord(axe: ABaxe) -> T.Tuple[T.Tuple[int, int], T.Tuple[int, int]]:
    ge = axe.spec
    gs = axe.figure.grid_spec
    sr, sc = ge.coord

    if isinstance(sr, int):
        start_r, stop_r = sr, sr
    else:
        start_r, stop_r, _ = sr.indices(gs.nrows)

    if isinstance(sc, int):
        start_c, stop_c = sc, sc
    else:
        start_c, stop_c, _ = sc.indices(gs.ncols)

    return (start_r, stop_r), (start_c, stop_c)


def gridspec_to_plotly_specs(gs: BGridSpec):
    # https://plotly.com/python/subplots/#multiple-custom-sized-subplots
    axe: ABaxe
    specs = [[None for _ in range(gs.ncols)] for _ in range(gs.nrows)]
    for axe in gs.figure.list_axes:
        (start_r, stop_r), (start_c, stop_c) = get_axe_coord(axe)

        if start_r == stop_r and start_c == stop_c:
            axe_spec = {}
        elif start_r < stop_r and start_c == stop_c:
            axe_spec = {"rowspan": stop_r - start_r}
        elif start_r == stop_r and start_c < stop_c:
            axe_spec = {"colspan": stop_c - start_c}
        elif start_r < stop_r and start_c < stop_c:
            axe_spec = {"rowspan": stop_r - start_r, "colspan": stop_c - start_c}

        specs[start_r][start_c] = axe_spec

    return specs


def simple_plotly_renderer(fig: BFigure) -> go.Figure:
    from plotly.subplots import make_subplots

    specs = gridspec_to_plotly_specs(fig.grid_spec)
    pfig = make_subplots(rows=fig.grid_spec.nrows, cols=fig.grid_spec.ncols, specs=specs)
    pfig.update_layout(title_text=fig.title)

    for axe in fig.list_axes:
        (start_r, stop_r), (start_c, stop_c) = get_axe_coord(axe)
        for plottable in axe.list_plottables:
            (
                xd,
                yd,
                name_of_x_var,
                unit_of_x_var,
                name_of_y_var,
                unit_of_y_var,
            ) = plottable._make_mline(axe)

            pfig.add_trace(go.Scatter(x=xd, y=yd, name=axe.title), row=start_r + 1, col=start_c + 1)

    pfig.show()


def test_generic_plot():
    x = np.array([1, 2])
    y = np.array([1, 2])

    fig = BFigure("Titre figure")
    gs = fig.add_gridspec(nrows=5, ncols=2)

    axe = fig.add_axe("Titre axe 1", spec=gs[0, 0])
    axe.plot((x, y))

    axe = fig.add_axe("Titre axe 2", spec=gs[0:2, 1])
    axe.plot((x, y))

    axe = fig.add_axe("Titre axe 3", spec=gs[1, 0])
    axe.plot((x, y))

    axe = fig.add_axe("Titre axe 4", spec=gs[2:4, 0:2])
    axe.plot((x, y))

    axe = fig.add_axe("Titre axe 5", spec=gs[4, 0])
    axe.plot((x, y))

    axe = fig.add_axe("Titre axe 6", spec=gs[4, 1])
    axe.plot((x, y))

    # mfig = simple_mpl_renderer(fig)
    mfig = simple_plotly_renderer(fig)

    return mfig


if __name__ == "__main__":
    test_generic_plot()
