import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import Select, HoverTool, ColumnDataSource
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc, figure
from collections import OrderedDict

SIZES = list(range(6, 22, 3))
COLORS = Spectral5
N_SIZES = len(SIZES)
N_COLORS = len(COLORS)

df = pd.read_json('processed_data.json')

ds = ColumnDataSource(df)

df = df.set_index(df['formula'])

columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]

def create_figure():
    xs = df[x.value].values
    ys = df[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()
    desc = list(df['formula'].values)

    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (x_title, y_title)

    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = 9
    if size.value != 'None':
        if len(set(df[size.value])) > N_SIZES:
            groups = pd.qcut(df[size.value].values, N_SIZES, duplicates='drop')
        else:
            groups = pd.Categorical(df[size.value])
        sz = [SIZES[xx] for xx in groups.codes]

    c = "#31AADE"
    if color.value != 'None':
        if len(set(df[color.value])) > N_COLORS:
            groups = pd.qcut(df[color.value].values, N_COLORS, duplicates='drop')
        else:
            groups = pd.Categorical(df[color.value])
        c = [COLORS[xx] for xx in groups.codes]

    source = ColumnDataSource(
    data=dict(
        x=xs,
        y=ys,
        desc=desc,
        col=c,
        siz=sz))

    TOOLTIPS = [
    ("(xx,yy)", "(@x, @y)"),
    ("label", "@desc"),
    ]

    p = figure(plot_height=600, plot_width=800, tooltips=TOOLTIPS, tools=['pan','box_zoom','hover','reset'], **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title


    p.circle('x','y', source=source, color='col', size='siz', line_color='white')#, , alpha=0.6, hover_color='white', hover_alpha=0.5)


    return p

def update(attr, old, new):
    layout.children[1] = create_figure()

x = Select(title='X-Axis', value='E_polaron_hole', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='E_polaron_electron', options=columns)
y.on_change('value', update)

size = Select(title='Size', value='p_eff_mass', options=['None'] + continuous)
size.on_change('value', update)

color = Select(title='Color', value='n_eff_mass', options=['None'] + continuous)
color.on_change('value', update)

controls = column([x, y, color, size], width=200)
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "Crossfilter"
