from tsne import Tsne
from plot import get_axis
from constants import tint
import matplotlib.pyplot as plt
from graph_helper import lighten_color


class Window:

    def __init__(self, tsne, esps, label_names, knn=None, example=None, title="TSNE"):
        self.tsne = Tsne(tsne, knn, example, title)
        self.fig = self.tsne.set_axes()
        self.esps = esps
        self.label_names = label_names

        self.train_widget, self.test_widget = self.tsne.set_plots()
        self.train_widget.on_clicked(self.select_esp_train)
        self.test_widget.on_clicked(self.select_esp_test)

        self.label_widget, self.knn_widget, self.slider_widget = self.tsne.set_widgets()
        self.label_widget.on_clicked(self.select_label)
        if self.tsne.knn != None:
            self.knn_widget.on_clicked(self.enable_knn)
            self.slider_widget.on_changed(self.update)

        self.set_colors_knn()

        self.fig.canvas.mpl_connect('pick_event', self.onpick)

    # check buttons

    def checklist(self, label, info):
        index = int(label)
        boolean = info[index].get_visible()
        info[index].set_visible(not boolean)

        self.fig.canvas.draw()

    def select_esp_train(self, label):
        self.checklist(label, self.tsne.train_scatter)

    def select_esp_test(self, label):
        self.checklist(label, self.tsne.test_scatter)

    def set_colors_knn(self):
        label_mode = 'labels' if self.label_widget.get_status()[
            0] else 'p_label'

        self.tsne.data[label_mode] = self.tsne.original_label_colors if self.label_widget.get_status()[
            0] else self.tsne.original_p_label_colors

        if self.tsne.knn_example != None:
            self.tsne.data.loc[self.tsne.knn_example, label_mode] = 'black'
            self.tsne.knn_artists[0].set_facecolor('black')

            for i, id in enumerate(self.tsne.knn_indices[:self.slider_widget.val]):
                self.tsne.data.loc[id, label_mode] = lighten_color(
                    self.tsne.data.loc[id, label_mode], tint[self.tsne.data.loc[id, 'mode']])
                self.tsne.knn_artists[i +
                                    1].set_facecolor(self.tsne.data.loc[id, label_mode])

        train = self.tsne.data[self.tsne.data["mode"] == 'train']
        test = self.tsne.data[self.tsne.data["mode"] == 'test']

        for id, scatter in self.tsne.train_scatter.items():
            scatter.set_facecolor(
                train[train["esp"] == id - 1][label_mode].tolist())

        for id, scatter in self.tsne.test_scatter.items():
            scatter.set_facecolor(
                test[test["esp"] == id - 1][label_mode].tolist())

        self.fig.canvas.draw()

    # check button for enabling real/predicted labels

    def select_label(self, label):
        self.set_colors_knn()

    # on click event
    # when clicked on point, gets artist responsible for creating it
    # gets list of indexes of artist and searches for id (order of creation)

    def onpick(self, event):
        indices = self.tsne.artists.get(event.artist)

        for id in event.ind:
            index = indices[id] if (type(indices) == list) else indices
            print(index)
            title = str(index) + " - " + str(self.label_names[index]) + " - ESP " + str(
                int(self.esps.loc[index]) + 1)

            fig, ax = plt.subplots()

            X, Y = get_axis(index)
            ax.plot(X, Y)
            ax.set_ylim(-0.01, 0.3)
            ax.grid()

            fig.canvas.manager.set_window_title(title)
            fig.show()

    # k number slider function

    def update(self, val):
        if self.tsne.knn_example != None:
            for index, item in self.tsne.knn_artists.items():
                item.set_visible(
                    index <= val and self.knn_widget.get_status()[0])

            self.set_colors_knn()

    # enable or disable knn only view

    def enable_knn(self, label):
        if self.tsne.knn_example != None:
            showing_knn = self.knn_widget.get_status()[0]

            for _, scatter in self.tsne.train_scatter.items():
                scatter.set_visible(not showing_knn)

            for _, scatter in self.tsne.test_scatter.items():
                scatter.set_visible(not showing_knn)

            for i, artist in self.tsne.knn_artists.items():
                artist.set_visible(showing_knn if i <=
                                   self.slider_widget.val else False)

            self.fig.canvas.draw()
