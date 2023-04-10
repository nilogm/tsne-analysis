from window import Window

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

path = "/home/hullo/tsne-analysis/sibling results"
data_path = "/home/hullo/OneDrive/NINFA/Dataset"

# features.csv
real_labels = pd.read_csv('%s/features_all.csv' % data_path,
                          sep=';', index_col='id')

# spectrum.npz
signals_data = np.load('%s/spectrum.npz' % data_path)

i = 1
while (i < 13):
    data = pd.read_csv(path + "/tsne/tsne_%d.csv" %
                       i, sep=',').set_index('index')
    data_tsne = Window(data.copy(), real_labels.esp_id, real_labels.label, data=real_labels)

    plt.axis('off')
    plt.show()

    i += 1
