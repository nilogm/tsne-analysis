import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Slider
import numpy as np
from graph_helper import create_ax, set_ax, create_legend, scatter
from constants import number_to_color_dict, marker_dict, name_to_color_dict, color_to_name_dict


class Tsne:
    def __init__(self, tsne, knn, index, title):
        self.knn = knn
        self.data = tsne
        self.set_variables()
        self.title = title

        self.knn_example = index
        if index != None:
            self.knn_indices = self.knn.loc[index].to_list()

        self.train_scatter = {}
        self.test_scatter = {}
        self.artists = {}
        self.knn_artists = {}

    def set_axes(self):
        # control window
        control_fig, axes = plt.subplot_mosaic("ABC;ABC;ABF;ABF;DDD;EEE")
        control_fig.canvas.manager.set_window_title("TSNE Manager")

        self.test_ax = set_ax(axes['A'], "Test")
        self.train_ax = set_ax(axes['B'], "Train")
        self.label_ax = set_ax(axes['C'])
        set_ax(axes['D'])
        if self.knn != None:
            self.knn_ax = set_ax(axes['E'])
            self.enable_knn_ax = set_ax(axes['F'])

        # tsne window
        fig, self.ax = plt.subplots()
        fig.canvas.manager.set_window_title(self.title)

        legend_esp_ax = create_ax(fig, [0, 0.95, 0.05, 0.05])
        create_legend(legend_esp_ax, "ESPs", "upper left",
                      marker_dict, **{"marker": 0})

        legend_ax = create_ax(fig, [0, 0, 0.05, 0.05])
        create_legend(legend_ax, "Labels", "lower left",
                      name_to_color_dict, **{"c": 0})
        # create_legend(legend_ax, "Labels", "lower left",
        #               number_to_color_dict, **{"c": 0})

        if self.knn_example != None:
            example_info = self.data.loc[self.knn_example]
            self.ax.set_title(str(self.knn_example) + " - " + color_to_name_dict[example_info['labels']] + " - ESP " + str(
                example_info['esp'] + 1) + " - (predicted: " + color_to_name_dict[example_info['p_label']] + ")")
            # self.ax.set_title(str(self.knn_example) + " - " + str(example_info['labels']) + " - ESP " + str(
            #     example_info['esp'] + 1) + " - (predicted: " + str(example_info['p_label']) + ")")

        return fig

    def set_variables(self):
        self.data['p_label'] = self.data['p_label'].map(number_to_color_dict)
        self.data['labels'] = self.data['labels'].map(number_to_color_dict)

        self.original_label_colors = self.data['labels']
        self.original_p_label_colors = self.data['p_label']

    def set_plots(self):
        train_buttons = self.set_scatterplot(
            self.train_ax, self.train_scatter, 'train', False)

        test_buttons = self.set_scatterplot(
            self.test_ax, self.test_scatter, 'test', True)

        if self.knn_example != None:
            all_knn = [self.knn_example] + self.knn_indices
            data_dict = {i: self.data.loc[index]
                        for i, index in enumerate(all_knn)}
            self.artists = scatter(
                self.ax, data_dict, self.knn_artists, self.artists, False)

        return train_buttons, test_buttons

    def set_widgets(self):
        label_buttons = CheckButtons(self.label_ax, ["Real Label"], [True])
        if self.knn != None:
            knn_buttons = CheckButtons(self.enable_knn_ax, ["Show KNN"], [False])
            slider = Slider(self.knn_ax, valmin=1, valmax=30, valinit=30,
                            label="K", valstep=[i for i in range(1, 31)])
            return label_buttons, knn_buttons, slider

        return label_buttons, None, None

    def set_scatterplot(self, ax, scatter_dict, mode, show=False):
        mode_data = self.data[self.data["mode"] == mode]
        mode_esps = np.unique(mode_data["esp"].to_list()) + 1

        buttons = CheckButtons(
            ax, mode_esps, [show for _ in range(len(mode_esps))])

        data_dict = {esp: mode_data[mode_data["esp"]
                                    == esp - 1] for esp in mode_esps}
        self.artists = scatter(
            self.ax, data_dict, scatter_dict, self.artists, show)

        return buttons
