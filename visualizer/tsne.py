import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Slider
import numpy as np
import pandas as pd
from graph_helper import create_ax, set_ax, create_legend, scatter, m_scatter
from constants import number_to_color_dict, marker_dict, name_to_color_dict, color_to_name_dict


class Tsne:
    def __init__(self, tsne, knn, index, title, real_data):
        self.data = tsne
        self.knn = knn
        self.title = title
        self.real_data = real_data

        self.data['labels'] = self.data['labels'].map(number_to_color_dict)
        self.data['p_label'] = self.data['p_label'].map(number_to_color_dict)

        self.label_colors = self.data['labels']
        self.p_label_colors = self.data['p_label']

        self.knn_example = index
        if index != None:
            self.knn_indices = self.knn.loc[index].to_list()

        self.train_scatter = {}
        self.test_scatter = {}
        self.artists = {}
        self.knn_artists = {}

        self.groups_scatter = {}

    def set_manager_window(self):
        """Sets all axes of manager window.
        """
        control_fig, axes = plt.subplot_mosaic("ABC;ABC;ABF;ABF;DDD;EEE")
        control_fig.canvas.manager.set_window_title("TSNE Manager")

        self.test_ax = set_ax(axes['A'], "Test")
        self.train_ax = set_ax(axes['B'], "Train")
        self.label_ax = set_ax(axes['C'])
        self.signal_ax = set_ax(axes['D'])
        self.knn_ax = set_ax(axes['E'])
        self.enable_knn_ax = set_ax(axes['F'])

    def set_tsne_window(self):
        """Sets plots of tsne window.

        Returns:
            fig: scatterplot's figure
        """
        fig, self.ax = plt.subplots()
        fig.canvas.manager.set_window_title(self.title)

        legend_esp_ax = create_ax(fig, [0, 0.95, 0.05, 0.05])
        create_legend(legend_esp_ax, "ESPs", "upper left",
                      marker_dict, **{"marker": 0})

        legend_label_ax = create_ax(fig, [0, 0, 0.05, 0.05])
        create_legend(legend_label_ax, "Labels", "lower left",
                      name_to_color_dict, **{"c": 0})

        if self.knn_example != None:
            example_info = self.data.loc[self.knn_example]
            self.ax.set_title(str(self.knn_example) + " - " + color_to_name_dict[example_info['labels']] + " - ESP " + str(
                example_info['esp'] + 1) + " - (predicted: " + color_to_name_dict[example_info['p_label']] + ")")

        return fig

    def set_plots(self):
        train_buttons = self.set_scatterplot(
            self.train_ax, self.train_scatter, 'train', False)

        test_buttons = self.set_scatterplot(
            self.test_ax, self.test_scatter, 'test', True)

        signal_buttons = self.set_group_buttons(self.signal_ax)
        self.set_groups(101)

        if self.knn_example != None:
            all_knn = [self.knn_example] + self.knn_indices
            data_dict = {i: self.data.loc[index]
                         for i, index in enumerate(all_knn)}
            self.artists = scatter(
                self.ax, data_dict, self.knn_artists, self.artists, False)

        return train_buttons, test_buttons, signal_buttons

    def set_widgets(self):
        label_toggle = CheckButtons(self.label_ax, ["Real Label"], [True])

        if self.knn != None:
            knn_buttons = CheckButtons(
                self.enable_knn_ax, ["Show KNN"], [False])
            slider = Slider(self.knn_ax, valmin=1, valmax=30, valinit=30,
                            label="K", valstep=[i for i in range(1, 31)])
            return label_toggle, knn_buttons, slider

        return label_toggle, None, None

    def set_scatterplot(self, ax, scatter_dict, mode, show=False):
        """Sets scatterplot of all points in "mode" and puts data in "scatter_dict".
        """
        mode_data = self.data[self.data["mode"] == mode]
        mode_esps = np.unique(mode_data["esp"].to_list()) + 1

        buttons = CheckButtons(
            ax, mode_esps, [show for _ in range(len(mode_esps))])

        data_dict = {esp: mode_data[mode_data["esp"]
                                    == esp - 1] for esp in mode_esps}
        scatter(self.ax, data_dict, scatter_dict, self.artists, show)

        return buttons

    def set_groups(self, signal_row, axis=None):
        self.groups_scatter.clear()
        same_row = self.real_data.loc[self.real_data["RPD row"] == signal_row]

        x = same_row.loc[same_row["RPD axis"] == "X"].index.to_list()
        y = same_row.loc[same_row["RPD axis"] == "Y"].index.to_list()

        indices = {
            "all": self.data.loc[x + y],
            "X": self.data.loc[x],
            "Y": self.data.loc[y],
        }

        m_scatter(self.ax, indices, self.groups_scatter, False)

    def set_group_buttons(self, ax):
        indices = ["all", "X", "Y"]

        buttons = CheckButtons(
            ax, indices, [False for _ in range(len(indices))])

        return buttons
