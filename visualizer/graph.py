from constants import markers, number_to_color_dict, name_to_color_dict, marker_dict
from graph_helper import lighten_color, disable_edges, create_ax, create_legend
from plot import get_axis

import matplotlib.pyplot as plt
from matplotlib.backend_bases import PickEvent
from matplotlib.collections import PathCollection
from matplotlib.artist import Artist
from matplotlib.figure import Figure
from matplotlib.widgets import CheckButtons

import pandas as pd

import threading
import time


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer != None:
            self._timer.cancel()
        self.is_running = False
        print("Stopped Animation")


class Graph:
    def __init__(self, data: pd.DataFrame, features: pd.DataFrame = None):
        """Initialize tsne analysis.
        Args:
            data (DataFrame): _description_
            features (DataFrame, optional): _description_. Defaults to None.
        """
        self.data = self.set_colors(data)
        self.features = features

    def set_colors(self, data: pd.DataFrame) -> pd.DataFrame:
        """Sets values to colors.
        Args:
            data (pd.DataFrame): DataFrame of information about tsne.
        Returns:
            pd.DataFrame: modified DataFrame with colors as labels.
        """
        self.real_colors = [name_to_color_dict[l] for l in data["label"]]
        self.real_labels = data["label"]
        data["label"] = self.real_colors

        self.predicted_colors = [number_to_color_dict[l] for l in data["p_label"]]
        data["p_label"] = self.predicted_colors

        return data

    def get_groups(self, esp=0) -> dict[int : list[int]]:
        """Returns all groups in analysis.
        Returns:
            dict: group name to indices
        """
        return {
            "train": self.data[self.data["esp"] != esp].index,
            "test": self.data[self.data["esp"] == esp].index,
            "group": None,
        }

    def reset_colors(self):
        """Resets scatterplot's colors to default."""

        def change_colors(scatter: dict[int, PathCollection], label="label"):
            """Switches colors between columns, indicated by "label".

            Args:
                scatter (dict[int : PathCollection]): esp to scatter dictionary.
                label (str, optional): DataFrame column with values. Defaults to "label".
            """
            for id, scat in scatter.items():
                scat.set_facecolor(self.data[self.data["esp"] == id][label])

        for _, graph in self.graphs.items():
            for g in graph:
                if g == None:
                    continue

                change_colors(g, "label" if self.display_real_labels else "p_label")

        self.fig.canvas.draw()

    def toggle_esp(self, esp: int, state: bool):
        """Toggles visibility of esp to all scatters.

        Args:
            esp (int): esp to be toggled.
            state (bool): state to set visibility to.
        """
        for i, (_, graph) in enumerate(self.graphs.items()):
            show = self.displayed_graph == i
            for g in graph:
                if g == None:
                    continue

                scatter = g.get(esp)
                if scatter == None:
                    continue

                scatter.set_visible(show & state)

        self.fig.canvas.draw()

    def set_graph(self, esp: int):
        """Sets the main window of the tsne analysis.

        Args:
            esp (int): test esp.
        """
        # fig = plt.figure(layout="constrained", figsize=[8.0, 6.0])
        fig, ax = plt.subplot_mosaic(
            [["tsne", "train"], ["tsne", "test"], ["tsne", "control"]],
            layout="constrained",
            width_ratios=[0.8, 0.2],
            height_ratios=[0.6, 0.1, 0.3],
            figsize=[8, 6],
        )

        self.fig = fig
        scatter_ax = ax["tsne"]

        all_esps = pd.unique(self.data["esp"])
        all_esps.sort()
        self.current_esp_visiblity = {i: i == esp for i in all_esps}

        groups = self.get_groups(esp)

        self.artist_recall: dict[
            Artist, tuple[dict[int, PathCollection], list[int]]
        ] = {}

        self.graphs = {
            "_0": self.set_scatters(scatter_ax, groups, info="_0"),
            "_50": self.set_scatters(scatter_ax, groups, info="_50"),
            "_100": self.set_scatters(scatter_ax, groups, info="_100"),
            "": self.set_scatters(scatter_ax, groups, show=True),
        }
        self.displayed_graph = len(self.graphs) - 1

        self.anim = self.set_animation(fig, scatter_ax)

        self.display_real_labels = False
        self.reset_colors()

        self.plot_signal = False
        self.selected_signal_info = None
        self.set_manager(ax, esp)

        def on_pick(event: PickEvent):
            self.select_signal_focus(
                event
            ) if self.plot_signal else self.select_signal_plot(event)

        fig.canvas.mpl_connect("close_event", lambda _: self.anim.stop())
        fig.canvas.mpl_connect("pick_event", lambda event: on_pick(event))

        legend_esp_ax = create_ax(fig, [0, 0.95, 0.05, 0.05])
        create_legend(legend_esp_ax, "ESPs", "upper left", marker_dict, **{"marker": 0})

        legend_label_ax = create_ax(fig, [0, 0, 0.05, 0.05])
        create_legend(
            legend_label_ax, "Labels", "lower left", name_to_color_dict, **{"c": 0}
        )

    def set_manager(self, ax: dict[plt.Axes], esp: int):
        """Sets the right side figure manager. Contains train and test toggle, animation, label and plot controls.

        Args:
            ax (dict[plt.Axes]): Ax dictionary.
            esp (int): Test esp.
        """
        for name, a in ax.items():
            if name == "tsne":
                continue
            disable_edges(a)

        def on_click_esp(label: str, dict: dict[int, int], buttons: CheckButtons):
            esp = int(label)
            state = buttons.get_status()[dict[esp]]
            self.current_esp_visiblity[esp] = state
            self.toggle_esp(esp - 1, state)

        def on_click_control(label: str, dict: dict[str, int], buttons: CheckButtons):
            state = buttons.get_status()[dict[label]]

            if label == "Select signal":
                self.plot_signal = state
            elif label == "Animate":
                self.anim.start() if state else self.anim.stop()
            elif label == "Real label":
                self.display_real_labels = state
                self.set_focus_to_groups()

        def set_buttons(
            ax: plt.Axes,
            title: str,
            labels: list[int | str],
            on_click_func,
            toggle=False,
        ):
            buttons = CheckButtons(ax, labels, [toggle for _ in range(len(labels))])
            buttons.on_clicked(
                lambda label: on_click_func(
                    label, {l: i for i, l in enumerate(labels)}, buttons
                )
            )
            ax.set_title(title)
            return buttons

        train_esps = pd.unique(self.data[self.data["esp"] != esp]["esp"]) + 1
        train_esps.sort()
        self.train_buttons = set_buttons(ax["train"], "Train", train_esps, on_click_esp)

        test_esps = pd.unique(self.data[self.data["esp"] == esp]["esp"]) + 1
        test_esps.sort()
        self.test_buttons = set_buttons(
            ax["test"], "Test", test_esps, on_click_esp, toggle=True
        )

        control_options = ["Select signal", "Animate", "Real label"]
        self.control_buttons = set_buttons(
            ax["control"], "Manager", control_options, on_click_control
        )

    def set_scatters(
        self, ax: plt.Axes, groups: dict[int : list[int]], info="", show=False
    ) -> tuple[dict[int, PathCollection], dict[int, PathCollection]]:
        """Sets train and test scatterplots.

        Args:
            ax (plt.Axes): .
            groups (dict[int : list[int]]): .
            info (str, optional): Additional info about selected columns. Defaults to "".
        """
        train_scatter = scatter(
            ax,
            self.data.loc[groups["train"]],
            recall=self.artist_recall,
            info=info,
            show=show,
            **{"picker": True, "pickradius": 5}
        )
        test_scatter = scatter(
            ax,
            self.data.loc[groups["test"]],
            recall=self.artist_recall,
            info=info,
            show=show,
            **{"picker": True, "pickradius": 5}
        )

        return train_scatter, test_scatter

    def set_animation(self, fig: Figure, ax: plt.Axes):
        """Sets epoch animation.

        Args:
            fig (Figure): .
        """

        def animate():
            self.displayed_graph += (
                1
                if self.displayed_graph < len(self.graphs) - 1
                else -len(self.graphs) + 1
            )

            for i, (info, graph) in enumerate(self.graphs.items()):
                show = self.displayed_graph == i
                if show:
                    title = (
                        "Now showing: " + info[1:] + " epochs"
                        if len(info) > 0
                        else "Now showing: final epoch"
                    )
                    ax.set_title(title)

                for g in graph:
                    if g == None:
                        continue
                    for esp, scatter in g.items():
                        scatter.set_visible(show & self.current_esp_visiblity[esp])

            fig.canvas.draw()

        anim = RepeatedTimer(2, animate)
        return anim

    def select_signal_focus(self, event: PickEvent):
        """Sets focus on selected point clicked signal.

        Args:
            event (PickEvent): .
        """
        indices = self.artist_recall.get(event.artist)
        if indices == None:
            return
        print("Artist found!")

        for id in event.ind:
            index = indices[id] if (type(indices) == list) else indices
            signal = self.features.loc[index, "RPD row"]
            esp = self.features.loc[index, "esp_id"]
            axis = self.features.loc[index, "RPD axis"]
            self.selected_signal_info = (esp, signal, axis)
            self.set_focus_to_groups()
            break

    def select_signal_plot(self, event: PickEvent):
        indices = self.artist_recall.get(event.artist)

        for id in event.ind:
            index = indices[id] if (type(indices) == list) else indices
            signal = self.features.loc[index, "RPD row"]
            esp = self.features.loc[index, "esp_id"]
            axis = self.features.loc[index, "RPD axis"]
            title = str(index) + " - ESP " + str(esp + 1) + " - " + str(signal) + axis

            fig, ax = plt.subplots()
            X, Y = get_axis(index)
            ax.plot(X, Y)
            ax.set_ylim(-0.01, 0.3)
            ax.grid()

            fig.canvas.manager.set_window_title(title)
            fig.show()

    def set_focus_to_groups(self):
        """Changes colors of all signals that belong ot the same group and axis (the other axis changes slightly)."""
        self.reset_colors()
        if self.selected_signal_info == None:
            return

        esp, signal, axis = self.selected_signal_info

        same_row = self.features.loc[self.features["RPD row"] == signal]
        same_axis = same_row.loc[same_row["RPD axis"] == axis].index

        selection = self.data.loc[self.data["esp"] == esp]
        for _, graph in self.graphs.items():
            col = "label" if self.display_real_labels else "p_label"
            for i in same_axis:
                selection.loc[i, col] = lighten_color(selection.loc[i, col], 0.6)

            for g in graph:
                if g == None:
                    continue
                if g.get(esp) == None:
                    continue

                g[esp].set_facecolor(selection[col])

        self.fig.canvas.draw()


def scatter(
    ax: plt.Axes,
    data: pd.DataFrame,
    tint=1,
    recall: dict[Artist, list[int]] = None,
    info="",
    show=False,
    **kwargs
) -> dict[int, PathCollection]:
    """Creates scatterplot of data and returns dictionary to each scatter.
    Data requires following columns "x", "y", "label" and "esp" (x and y can be altered with "info").

    Args:
        data (pd.DataFrame): DataFrame with info abou tsne (x, y, label, esp).
        tint (int, optional): Defaults to 1.
        recall (dict[Artist, list[int]], optional): Artist to index dictionary to enable interaction with picker. Defaults to None.
        info (str, optional): Additional information to columns x and y.

    Returns:
        dict[int, PathCollection]: esp to scatter dictionary.
    """
    esp_to_scatter = {}
    for esp in pd.unique(data["esp"]):
        selection: pd.DataFrame = data[data["esp"] == esp]
        m = markers[esp - 1]

        if tint < 1:
            for index, row in selection.iterrows():
                selection.at[index, "label"] = lighten_color(row["label"], tint)

        s = ax.scatter(
            data=selection,
            x="x" + info,
            y="y" + info,
            c="label",
            edgecolors="black",
            linewidths=0.5,
            marker=m,
            s=70,
            **kwargs
        )
        s.set_visible(show)

        if recall != None:
            obj = selection.index.tolist()
            recall.update({s.findobj()[0]: obj})

        esp_to_scatter.update({esp: s})

    return esp_to_scatter


if __name__ == "__main__":
    path = "C:/Users/nilox/tsne-analysis/results/test1"
    data_path = "C:/Users/nilox/OneDrive/NINFA/Dataset/"

    esp = 1

    data = pd.read_csv(path + "/tsne/tsne_%d.csv" % esp, sep=",").set_index("index")
    features = pd.read_csv(data_path + "/features_all.csv", sep=";").set_index("id")

    a = Graph(data.copy(), features=features)
    a.set_graph(esp - 1)

    plt.show()
