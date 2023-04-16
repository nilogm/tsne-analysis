from tsne import Tsne
from plot import get_axis
from constants import tint
import matplotlib.pyplot as plt
from graph_helper import lighten_color


class Window:
    def __init__(
        self,
        tsne,
        esps,
        label_names,
        data=None,
        knn=None,
        example=None,
        title="TSNE",
        esp=0,
    ):
        self.tsne = Tsne(
            tsne[["label", "esp", "p_label", "x", "y"]].copy(),
            knn,
            example,
            title,
            data,
        )
        self.tsne.set_manager_window()
        self.fig = self.tsne.set_tsne_window()
        self.esps = esps
        self.label_names = label_names

        amount_of_epochs = int((len(tsne.columns) - 3) / 3) - 1
        self.tsne_dict = {
            str(i * 50): Tsne(
                tsne[
                    [
                        "label",
                        "esp",
                        "p_label_" + str(i * 50),
                        "x_" + str(i * 50),
                        "y_" + str(i * 50),
                    ]
                ].copy(),
                None,
                None,
                title,
                data,
                info="_" + str(i * 50),
                esp=esp,
            )
            for i in range(amount_of_epochs)
        }
        self.esp = esp
        # for _, item in self.tsne_dict.items():
        #     item.set_manager_window()
        #     item.set_tsne_window()

        self.data = data

        self.train_widget, self.test_widget, self.signal_widget = self.tsne.set_plots()
        self.train_widget.on_clicked(
            lambda label: self.toggle_visibility(label, self.tsne.train_scatter)
        )
        self.test_widget.on_clicked(
            lambda label: self.toggle_visibility(label, self.tsne.test_scatter)
        )
        self.signal_widget.on_clicked(
            lambda label: self.toggle_visibility(label, self.tsne.groups_scatter)
        )

        (
            self.control_panel,
            self.knn_widget,
            self.slider_widget,
        ) = self.tsne.set_widgets()
        self.control_panel.on_clicked(self.set_interaction)
        if self.tsne.knn != None:
            self.knn_widget.on_clicked(self.toggle_knn)
            self.slider_widget.on_changed(self.slider_update)

        self.get_signal_state = False

        self.set_colors_knn()

        self.fig.canvas.mpl_connect("pick_event", self.on_click)

    # check buttons

    def toggle_visibility(self, label, info):
        """Given the label, toggle visibility of group.

        Args:
            label (int): button label
            info (dict): group to items dictionary
        """
        if info == None:
            return

        index = label if label == "all" or label == "X" or label == "Y" else int(label)
        info[index].set_visible(not (info[index].get_visible()))
        self.fig.canvas.draw()

    def set_colors(self, scatter, label_mode, same=False):
        """Sets the color of scatter based on tag and label.

        Args:
            tag (str): mode to extract data from
            scatter (dict): esp to scatter dictionary
            label_mode (str): label mode (real/predicted)
        """
        if same:
            data = self.tsne.data[self.tsne.data["esp"] == self.esp]
        else:
            data = self.tsne.data[self.tsne.data["esp"] != self.esp]
        for id, scat in scatter.items():
            scat.set_facecolor(data[data["esp"] == id - 1][label_mode].tolist())

    def set_interaction(self, label):
        if label == "Real Label":
            self.set_colors_knn()
        elif label == "Get Signal":
            self.get_signal_state = self.control_panel.get_status()[1]
        elif label == "Start Animation":
            pass

    def set_colors_knn(self):
        """Sets the colors of all scatters."""
        real_label = self.control_panel.get_status()[0]
        label_mode = "labels" if real_label else "p_label"
        self.tsne.data[label_mode] = (
            self.tsne.label_colors if real_label else self.tsne.p_label_colors
        )

        if self.tsne.knn_example != None:
            pass
            # self.tsne.data.loc[self.tsne.knn_example, label_mode] = 'black'
            # self.tsne.knn_artists[0].set_facecolor('black')

            # for i, id in enumerate(self.tsne.knn_indices[:self.slider_widget.val]):
            #     self.tsne.data.loc[id, label_mode] = lighten_color(
            #         self.tsne.data.loc[id, label_mode], tint[self.tsne.data.loc[id, 'mode']])
            #     self.tsne.knn_artists[i +
            #                           1].set_facecolor(self.tsne.data.loc[id, label_mode])

        self.set_colors("train", self.tsne.train_scatter, label_mode)
        self.set_colors("test", self.tsne.test_scatter, label_mode)

        self.fig.canvas.draw()

    # on click event
    # when clicked on point, gets artist responsible for creating it
    # gets list of indexes of artist and searches for id (order of creation)

    def on_click(self, event):
        if self.get_signal_state:
            self.get_signal(event)
        else:
            self.show_graph(event)

    def get_signal(self, event):
        """Gets signal of clicked point."""
        indices = self.tsne.artists.get(event.artist)

        for id in event.ind:
            index = indices[id] if (type(indices) == list) else indices
            signal = self.data.loc[index, "RPD row"]
            self.tsne.set_groups(signal)
            break

    def show_graph(self, event):
        """Show graph of picked signal based on event.

        Args:
            event ():
        """
        indices = self.tsne.artists.get(event.artist)

        for id in event.ind:
            index = indices[id] if (type(indices) == list) else indices

            label = str(self.label_names[index])
            esp_id = str(int(self.esps.loc[index]) + 1)
            signal = str(self.data.loc[index, "RPD row"])
            axis = "X" if self.data.loc[index, "RPD axis"] == 0 else "Y"
            title = (
                str(index) + " - " + label + " - ESP " + esp_id + " - " + signal + axis
            )

            self.tsne.set_groups(int(signal))

            fig, ax = plt.subplots()

            X, Y = get_axis(index)
            ax.plot(X, Y)
            ax.set_ylim(-0.01, 0.3)
            ax.grid()

            fig.canvas.manager.set_window_title(title)
            fig.show()

    def slider_update(self, k):
        """Updates visibility of knn based on slider value.

        Args:
            k (int): amount of neighbors
        """
        for index, item in self.tsne.knn_artists.items():
            item.set_visible(index <= k and self.knn_widget.get_status()[0])

        self.set_colors_knn()

    def enable_scatter(self, scatter, bool):
        """Toggles visibility of scatter.

        Args:
            scatter (dict): esp to scatter dictionary
            bool (bool): state to change to
        """
        for _, s in scatter.items():
            s.set_visible(bool)

    def toggle_knn(self):
        """Toggles visibility to display all or only knn tsne."""
        showing_knn = self.knn_widget.get_status()[0]

        self.enable_scatter(self, self.tsne.train_scatter, not showing_knn)
        self.enable_scatter(self, self.tsne.test_scatter, not showing_knn)

        for i, artist in self.tsne.knn_artists.items():
            artist.set_visible(showing_knn if i <= self.slider_widget.val else False)

        self.fig.canvas.draw()
