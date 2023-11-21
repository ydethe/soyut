import numpy as np

from soyut.frontend.BFigure import BFigure


def test_generic_plot():
    x = np.arange(10)
    y = np.cos(x)

    fig = BFigure("Titre figure")
    gs = fig.add_gridspec(nrow=2, ncol=1)

    axe = fig.add_axe("Titre axe 1", spec=gs[0, 0])
    axe.plot((x, y))


if __name__ == "__main__":
    test_generic_plot()
