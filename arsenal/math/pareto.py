"""
Pareto frontier
"""
import pylab as pl
import numpy as np
from arsenal.terminal import yellow
from arsenal.iterextras import window


def pareto_frontier(X, Y, maxX=True, maxY=True):
    """Determine Pareto frontier, returns list of sorted points.

    Args:

      X, Y: data.

      maxX, maxY: (bool) whether to maximize or minimize along respective
        coordinate.

    """
    assert len(X) == len(Y)
    if len(X) == 0:
        return []
    a = sorted(zip(X, Y), reverse=maxX)
    frontier = []
    _, lasty = a[0]
    for xy in a:
        _,y = xy
        if maxY:
            if y >= lasty:
                frontier.append(xy)
                lasty = y
        else:
            if y <= lasty:
                frontier.append(xy)
                lasty = y
    return frontier


def pareto_ix(X, Y, maxX=True, maxY=True):
    """Determine Pareto frontier, returns list of indices

    Args:

      X, Y: data.

      maxX, maxY: (bool) whether to maximize or minimize along respective
        coordinate.

    """
    assert len(X) == len(Y)
    if len(X) == 0:
        return []
    a = sorted(zip(X, Y, range(len(X))), reverse=maxX)
    frontier = []
    [_, lasty, _] = a[0]
    for xyi in a:
        _,y,i = xyi
        if maxY:
            if y >= lasty:
                frontier.append(i)
                lasty = y
        else:
            if y <= lasty:
                frontier.append(i)
                lasty = y
    return frontier


def show_frontier(X, Y, maxX=False, maxY=True, dots=False,
                  XMAX=None, YMIN=None, ax=None, label=None, **style):
    """Plot Pareto frontier.

    Args:

      X, Y: data.

      maxX, maxY: (bool) whether to maximize or minimize along respective
        coordinate.

      dots: (bool) highlight points on the frontier (will use same color as
        `style`).

      ax: use an existing axis if non-null.

      style: keyword arguments, which will be passed to lines connecting the
        points on the Pareto frontier.

      XMAX: max value along x-axis
      YMIN: min value along y-axis

    """
    if ax is None:
        ax = pl.gca()
    sty = {'c': 'b', 'alpha': 0.3, 'zorder': 0}
    sty.update(style)

    assert not maxX and maxY, 'need to update some hardcoded logic'

    f = pareto_frontier(X, Y, maxX=maxX, maxY=maxY)
    if not f:
        print yellow % '[warn] Empty frontier'
        return
    if dots:
        xs, ys = zip(*f)
        ax.scatter(xs, ys, lw=0, alpha=0.5, c=sty['c'])

    XMAX = XMAX if XMAX is not None else max(X)
    YMIN = YMIN if YMIN is not None else min(Y)
    assert XMAX >= max(X)
    assert YMIN <= min(Y)

    # Connect corners of frontier. The first and last points on frontier have
    # lines which surround the point cloud.
    f = [(min(X), YMIN)] + f + [(XMAX, max(Y))]

    # Make line segments from adjacent points
    pts = np.array([x for ((a,b), (c,d)) in window(f, 2) for x in [[a,b], [c,b], [c,b], [c,d]]])

    # Plot
    ax.plot(pts[:,0], pts[:,1], label=label, **sty)


class Pareto(object):

    def __init__(self, df, xcol, ycol, ax=None):
        self.df = df
        self.xcol = xcol
        self.ycol = ycol
        self.ax = ax
        self.frontier = pareto_ix(df[xcol], df[ycol])
        assert np.isfinite(df[xcol]).all() and np.isfinite(df[ycol]).all(), \
            'Pareto: `DataFrame` contains non-finite values.'

    def scatter(self, **plot_kwargs):
        if self.ax is None:
            self.ax = pl.gca()
        kwargs = dict(lw=0)
        kwargs.update(plot_kwargs)
        self.ax.scatter(self.df[self.xcol], self.df[self.ycol], **kwargs)

    def show_frontier(self, **plot_kwargs):
        if self.ax is None:
            self.ax = pl.gca()
        show_frontier(self.df[self.xcol], self.df[self.ycol], ax=self.ax, **plot_kwargs)

    def lookup_x(self, x):
        s = self.df
        s = s[s[self.xcol] <= x]    # filter
        if s.empty:
            return np.nan
        yy = s[self.ycol].argmax()
        return s.ix[yy][self.ycol]

    def lookup_y(self, y):
        s = self.df
        s = s[s[self.ycol] >= y]    # filter
        if s.empty:
            return np.nan
        xx = s[self.xcol].argmin()
        return s.ix[xx][self.xcol]


def test():
    from pandas import DataFrame
    X = np.linspace(0.01, 1.0, 10)
    Y = np.log(X)
    Y -= Y.min()
    Y /= Y.max()
    Y *= 0.95

    #Y = X

    df = DataFrame({'X': X, 'Y': Y})
    P = Pareto(df, 'X', 'Y')

    data = []
    for val in np.linspace(0,1,15):
        data.append(dict(val=val, x=P.lookup_x(val), y=P.lookup_y(val)))
        pl.axvline(val, alpha=.5)
        pl.axhline(val, alpha=.5)
    dd = DataFrame(data)
    pl.scatter(dd.y, dd.val, lw=0, c='r')
    pl.scatter(dd.val, dd.x, lw=0, c='g')
    print dd

    #P.scatter(c='r', lw=0)
    P.show_frontier(c='r', lw=4)
    pl.show()


if __name__ == '__main__':
    test()
