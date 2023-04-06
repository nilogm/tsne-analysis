from constants import markers
import pandas as pd


def disable_edges(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])


def create_ax(fig, size=[0.0, 0.0, 0.0, 0.0], title=""):
    ax = fig.add_axes(size)
    disable_edges(ax)
    ax.set_title(title)
    return ax


def set_ax(ax, title=""):
    disable_edges(ax)
    ax.set_title(title)
    return ax


def create_legend(ax, title, position, dict, **kwargs):
    a = []

    for item, form in dict.items():
        for key, _ in kwargs.items():
            kwargs[key] = form
        a += [ax.scatter(0, 0, label=item, edgecolors='black',
                         linewidths=0.8, **kwargs)]

    ax.legend(title=title, loc=position)

    for item in a:
        item.set_visible(False)


def scatter(ax, data_dict, scatter_list, artist_dict, show=False):
    for key, item in data_dict.items():
        m = markers[item.esp.astype(int)] if (
            type(item) == pd.Series) else markers[int(item["esp"].iloc[0])]

        scatter = ax.scatter(data=item, x="x", y="y", c="labels", edgecolors='black',
                             linewidths=0.5, marker=m, s=70, picker=True, pickradius=5)
        scatter.set_visible(show)

        obj = item.index.tolist() if isinstance(item, pd.DataFrame) else item.name
        artist_dict.update(
            {scatter.findobj()[0]: obj})
        scatter_list.update({key: scatter})

    return artist_dict

# https://stackoverflow.com/questions/37765197/darken-or-lighten-a-color-in-matplotlib


def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return mc.to_hex(colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2]))
