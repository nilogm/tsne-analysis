from window import Window

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

path = "/home/ngmonteiro/ESPset-normal/sibling results"

# features.csv
real_labels = pd.read_csv('/home/ngmonteiro/RPDBCS/features_all.csv',
                          sep=';', index_col='id')

# spectrum.npz
signals_data = np.load('/home/ngmonteiro/RPDBCS/spectrum.npz')

i = 1
while (i < 13):
    data = pd.read_csv(path + "/tsne/tsne_%d.csv" %
                       i, sep=',').set_index('index')
    data_tsne = Window(data.copy(), real_labels.esp_id, real_labels.label, data=real_labels)

    plt.axis('off')
    plt.show()

    i += 1
