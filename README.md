# ZoomedInsetAxis

![Example image](https://github.com/hatfullr/ZoomedInsetAxis/blob/main/all_solutions_with_particles_Galaviz_Tr_take4.png)

This is a function that can be used with matplotlib for Python 3+ to create an inset axis that is a zoomed-in version of the parent axis, inspired by the `ax.inset_axis`. You can import it as,
```
from ZoomedInsetAxis import zoomed_inset_axis
```
Then, call it using,
```
zoomed_inset_axis(ax,((x0,y0),(x1,y1)))
```
where `ax` is the axis you want to zoom in on and `x0`, `y0`, `x1`, and `y1` are the data coordiantes.

This function currently only supports zooming in on axes which contain `Line2D` and `PathCollection` objects, which are created by `plt.plot` and `plt.scatter`, respectively. It is not guaranteed that the zoomed-in axis will be an exact copy of the parent axis, but it is pretty darn close. After the axis is created, you can work on it as with any regular matplotlib `Axes` object.

By default, the zoomed-in axis has no tick labels and its tick marks correspond to that of the parent axis.

You can specify the zoom level using the keyword `zoom` (default is 2), which takes either a 2-tuple, float, or integer. If a 2-tuple is specified, the inset axis will be zoomed in by a factor of `zoom[0]` on the x-axis and `zoom[1]` on the y-axis. Otherwise, both axes will be zoomed by a factor of `zoom`. 

You can specify where you want the inset axis placed with the `loc` keyword, which accepts values, `'upper left','upper right','lower left','lower right'`, or `0,1,2,3` correspondingly.

You can change the padding the inset axis has with the parent axis with the `borderaxespad` keyword, which accepts a 2-tuple, float, or integer measured as fraction of the parent axis. The default value is `(matplotlib.rcParams['axes.xmargin'],matplotlib.rcParams['axes.ymargin'])`.
