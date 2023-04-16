from window import Window

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

path = "C:/Users/nilox/tsne-analysis/test tsne"
data_path = "C:/Users/nilox/OneDrive/NINFA/Dataset"

# features.csv
real_labels = pd.read_csv("%s/features_all.csv" % data_path, sep=";", index_col="id")

# spectrum.npz
signals_data = np.load("%s/spectrum.npz" % data_path)

i = 5
while i < 13:
    data = pd.read_csv(path + "/tsne/tsne_%d.csv" % i, sep=",").set_index("index")
    data_tsne = Window(
        data.copy(), real_labels.esp_id, real_labels.label, data=real_labels, esp=i
    )

    plt.axis("off")
    plt.show()

    i += 1
