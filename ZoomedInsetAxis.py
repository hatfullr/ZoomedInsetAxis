import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import matplotlib as mpl
import numpy as np
import inspect

# This makes an inset axis on the input ax. The inset axis is zoomed
# in to the input data limits.

def zoomed_inset_axis(ax,
                      data_bounds,
                      zoom=(2.,2.),
                      loc='lower right',
                      borderaxespad=(mpl.rcParams['axes.xmargin'],mpl.rcParams['axes.ymargin']),
                      *args,**kwargs):
    # 'data_bounds' is ((xmin,ymin),(xmax,ymax)) in data coordinates
    # 'loc' can be one of 'upper left', 'upper right', 'lower left', 'lower right',
    # or 0, 1, 2, 3 respectively, or any (x0,y0) tuple. If 'loc' is a tuple,
    # 'borderaxespad' is set to (0,0)
    # 'borderaxespad' is a tuple of 2 values, measured in fractions of the axis x and y dimensions
    # uses mpl.rcParams['axes.xmargin'] and mpl.rcParams['axes.ymargin'] by default
    if isinstance(borderaxespad,(float,int)): borderaxespad = (borderaxespad,borderaxespad)
    if isinstance(zoom,(float,int)): zoom = (zoom,zoom)
        
    possible_loc = ['upper left','upper right','lower left','lower right']
    if isinstance(loc,(tuple,list)):
        x0 = loc[0]
        y0 = loc[1]
        borderaxespad=(0,0)
    elif isinstance(loc,int):
        loc = possible_loc[loc]

    fig = ax.get_figure()

    canvas = fig.canvas
    renderer = canvas.get_renderer()
    figsize = fig.get_size_inches()
    trans = ax.transAxes.inverted()

    data_bounds_ax = ax.transAxes.inverted().transform(ax.transData.transform(data_bounds))
    width = abs(data_bounds_ax[1][0]-data_bounds_ax[0][0])*zoom[0]
    height = abs(data_bounds_ax[1][1]-data_bounds_ax[0][1])*zoom[1]


    canvas.draw()

    axpos = fig.transFigure.inverted().transform(ax.get_window_extent(renderer=renderer))
    axsize_inches = ((axpos[1][0]-axpos[0][0])*figsize[0],(axpos[1][1]-axpos[0][1])*figsize[1])

    max_tick_ax = np.array([[0.,0.],[0.,0.]])
    if loc in possible_loc:
        for tick in ax.xaxis.get_major_ticks():
            if tick.get_tickdir() == 'in':
                if 'lower' in loc and tick.tick1line.get_visible(): max_tick_ax[0][0] = max(max_tick_ax[0][0],tick._size)
                elif 'upper' in loc and tick.tick2line.get_visible(): max_tick_ax[0][1] = max(max_tick_ax[0][1],tick._size)
        for tick in ax.yaxis.get_major_ticks():
            if tick.get_tickdir() == 'in':
                if 'left' in loc and tick.tick1line.get_visible(): max_tick_ax[1][0] = max(max_tick_ax[1][0],tick._size)
                elif 'right' in loc and tick.tick2line.get_visible(): max_tick_ax[1][1] = max(max_tick_ax[1][1],tick._size)

    max_tick_self = np.array([[0.,0.],[0.,0.]])
    if mpl.rcParams['xtick.direction'] == 'out':
        for i,b in enumerate([mpl.rcParams['xtick.bottom'],mpl.rcParams['xtick.top']]):
            if b:
                max_tick_self[1][i] = max(max_tick_self[1][i],mpl.rcParams['xtick.major.size'])
                if mpl.rcParams['xtick.minor.visible']:
                    max_tick_self[1][i] = max(max_tick_self[1][i],mpl.rcParams['xtick.minor.size'])
    if mpl.rcParams['ytick.direction'] == 'out':
        for i,b in enumerate([mpl.rcParams['ytick.left'],mpl.rcParams['ytick.right']]):
            if b:
                max_tick_self[0][i] = max(max_tick_self[0][i],mpl.rcParams['ytick.major.size'])
                if mpl.rcParams['ytick.minor.visible']:
                    max_tick_self[0][i] = max(max_tick_self[0][i],mpl.rcParams['ytick.minor.size'])

    # [ [bottom, top], [left, right] ]
    max_tick_diff = np.array(max_tick_ax) + np.array(max_tick_self) # In points
    max_tick_diff[0] /= 72.*axsize_inches[1]
    max_tick_diff[1] /= 72.*axsize_inches[0]

    self_lw = mpl.rcParams['axes.linewidth']/72.

    if 'left' in loc:
        x0 = borderaxespad[0]+max_tick_diff[1][0]+(self_lw/axsize_inches[0])
    elif 'right' in loc:
        x0 = 1.-borderaxespad[0]-max_tick_diff[1][1]-width # No lw adjustment here (quirk of matplotlib)
    if 'upper' in loc:
        y0 = 1.-borderaxespad[1]-max_tick_diff[0][1]-height-(self_lw/axsize_inches[1])
    elif 'lower' in loc:
        y0 = borderaxespad[1]+max_tick_diff[0][0] # No lw adjustment here (quirk of matplotlib)


    # Now we need to draw all the axis children onto our new axis
    old_artists = []
    for child in ax.get_children():
        if child in [ax.xaxis,ax.yaxis]: continue
        if type(child).__name__ == 'Text':
            if not child.get_text() or child.get_text().isempty(): continue
        elif type(child).__name__ == 'Rectangle':
            bbox = child.get_bbox()
            if bbox.x0 == 0 and bbox.y0 == 0 and bbox.x1 == 1 and bbox.y1 == 1: continue
        elif type(child).__name__ == 'Spine': continue

        elif type(child).__name__ in ['Line2D','PathCollection']: # [ax.plot,ax.scatter]
            old_artists.append(child)

    # Create the inset axis
    inset_ax = ax.inset_axes([x0,y0,width,height],*args,**kwargs)
    ax = inset_ax.axes # Re-find the axis this belongs to


    # Do our best to re-plot everything
    new_artists = []
    for old_artist in old_artists:
        if type(old_artist).__name__ == 'Line2D': # Guess that this is an ax.plot object
            properties = old_artist.properties()
            
            kwargs = {}
            kwargs['color']=properties['color']
            kwargs['linestyle']=properties['linestyle']
            kwargs['linewidth']=properties['linewidth']
            kwargs['marker']=properties['marker']
            kwargs['markeredgecolor']=properties['markeredgecolor']
            kwargs['markeredgewidth']=properties['markeredgewidth']
            kwargs['markerfacecolor']=properties['markerfacecolor']
            kwargs['markerfacecoloralt']=properties['markerfacecoloralt']
            kwargs['markersize']=properties['markersize']
            kwargs['markevery']=properties['markevery']
            kwargs['path_effects']=properties['path_effects']
            kwargs['dash_capstyle']=properties['dash_capstyle']
            kwargs['dash_joinstyle']=properties['dash_joinstyle']
            kwargs['picker']=properties['picker']
            kwargs['pickradius']=properties['pickradius']
            kwargs['rasterized']=properties['rasterized']
            kwargs['sketch_params']=properties['sketch_params']
            kwargs['snap']=properties['snap']
            kwargs['solid_capstyle']=properties['solid_capstyle']
            kwargs['solid_joinstyle']=properties['solid_joinstyle']
            kwargs['drawstyle']=properties['drawstyle']
            kwargs['fillstyle']=properties['fillstyle']
            kwargs['label']=properties['label']
            kwargs['alpha']=properties['alpha']
            kwargs['url']=properties['url']
            kwargs['visible']=properties['visible']
            kwargs['zorder']=properties['zorder']

            xdata = properties['xdata']
            ydata = properties['ydata']

            args = [xdata,ydata]
            method = inset_ax.plot
            if len(xdata) == 2 and (0. in xdata and 1. in xdata) and len(np.unique(ydata)) == 1: # This is an axhline
                method = inset_ax.axhline
                args = [ydata[0]]
            if len(ydata) == 2 and (0. in ydata and 1. in ydata) and len(np.unique(xdata)) == 1: # This is an axvline
                method = inset_ax.axvline
                args = [xdata[0]]
            
            result = method(*args,**kwargs)
            if not isinstance(result,(list,tuple,np.ndarray)):
                new_artists.append(result)
            else:
                for element in result: new_artists.append(element)
                
        elif type(old_artist).__name__ == 'PathCollection': # Guess that this is an ax.scatter object
            properties = old_artist.properties()
            offsets = properties['offsets']
            new_artists.append(inset_ax.scatter(offsets[:,0],offsets[:,1],
                                            c=properties['array'],
                                            cmap=properties['cmap'],
                                            vmin=properties['clim'][0],
                                            vmax=properties['clim'][1],
                                            s=properties['sizes'],
                                            label=properties['label'],
                                            alpha=properties['alpha'],
                                            zorder=properties['zorder'],
                                            edgecolor=None if properties['array'] is None or any(properties['array']) else properties['edgecolor'],
                                            facecolor=properties['facecolor'],
                                            hatch=properties['hatch'],
                                            linestyle=properties['linestyle'],
                                            linewidth=properties['linewidth'],
                                            path_effects=properties['path_effects'],
                                            picker=properties['picker'],
                                            pickradius=properties['pickradius'],
                                            rasterized=properties['rasterized'],
                                            sketch_params=properties['sketch_params'],
                                            snap=properties['snap'],
                                            url=properties['url'],
                                            urls=properties['urls'],
                                            visible=properties['visible']))

    #inset_ax._animated = False
    #for new_artist in new_artists:
    #    if new_artist.properties()['animated']:
    #        inset_ax._animated = True

    # Copy over all the attributes
    """
    for old_artist,new_artist in zip(old_artists,new_artists):

        dirold_artist = dir(old_artist)
        dirnew_artist = dir(new_artist)
        for attr in dirold_artist: # attr is "get"
            asplit = attr.split("_")
            if asplit[0] == 'get': # Check for a set command
                for a in dirold_artist: # a is "set"
                    asplit2 = a.split("_")
                    if asplit2[0] == 'set' and asplit[1:] is asplit2[1:]:
                        getattr(new_artist,attr)(getattr(child,a)())
    """

    inset_ax.set_xticklabels('')
    inset_ax.set_yticklabels('')

    major_xticks = inset_ax.axes.get_xticks(minor=False)
    major_yticks = inset_ax.axes.get_yticks(minor=False)
    minor_xticks = inset_ax.axes.get_xticks(minor=True)
    minor_yticks = inset_ax.axes.get_yticks(minor=True)

    inset_ax.set_xticks(major_xticks,minor=False)
    inset_ax.set_xticks(minor_xticks,minor=True)
    inset_ax.set_yticks(major_yticks,minor=False)
    inset_ax.set_yticks(minor_yticks,minor=True)

    inset_ax.set_xlim((data_bounds[0][0],data_bounds[1][0]))
    inset_ax.set_ylim((data_bounds[0][1],data_bounds[1][1]))

    inset_ax.axes.indicate_inset_zoom(inset_ax)
    return inset_ax
        
        
"""
# Test
plt.style.use('supermongo')
fig, ax = plt.subplots(figsize=(8.,8.))

ax.plot([0,1],[0,0])
ax.scatter([0,1],[0,0])
ax.set_xlim((ax.get_xlim()[0],0.8))
inset_ax = ZoomedInsetAxis(ax,((-0.01,-0.0001),(0.2,0.0001)),loc='lower right',borderaxespad=(0,0))



plt.show()
"""
