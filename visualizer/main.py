from window import Window

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

path = "/home/ngmonteiro/ESPset-normal/sibling results"

# features.csv
real_labels = pd.read_csv('/home/ngmonteiro/RPDBCS/features_all.csv',
                          sep=';', index_col='id', usecols=['id', 'label', 'esp_id', 'label_id'])

# spectrum.npz
signals_data = np.load(
    '/home/ngmonteiro/RPDBCS/spectrum.npz')

# bias_knn = pd.read_csv(path + "/knn/knn_1.csv", index_col=0)
# data = pd.read_csv(path + "/tsne/tsne_1.csv",
#                         sep=',').set_index('index')


# no_bias_knn = pd.read_csv(path + "/knn/no_bias/knn_2.csv", index_col=0)
# no_bias_data = pd.read_csv(
#     path + "/tsne/no_bias/tsne_2.csv", sep=',').set_index('index')

# esp id
# esp = no_bias_data.loc[no_bias_knn.index[0]]["esp"]

# specific label
# examples = bias_data[bias_data["esp"] == esp][bias_data["labels"]
#                                               == 4][bias_data['mode'] == 'test'].index

# different prediction
# all_indices = bias_data[bias_data["esp"] ==
#                         esp][bias_data['mode'] == 'test'].index
# no_bias_test = no_bias_data[no_bias_data['mode'] == 'test'].loc[all_indices]
# alternate_examples = no_bias_test[no_bias_test['p_label']
#                                   != bias_data.loc[all_indices]['p_label']].index

# specific label
# alternate_examples = no_bias_test[no_bias_test['p_label'] != bias_data.loc[all_indices]['p_label']][no_bias_test['labels'] == 0].index

# all no bias examples
# alternate_examples = bias_data[bias_data["esp"] == esp][bias_data['mode'] == 'test'].index
# alternate_examples = bias_data[bias_data["esp"] == esp][bias_data['mode'] == 'test'][bias_data['labels'] == 1].index


i = 1
while (i < 13):
    # index = alternate_examples[i]
    
    data = pd.read_csv(path + "/tsne/tsne_%d.csv" % i, sep=',').set_index('index')
    data_tsne = Window(data.copy(), real_labels.esp_id, real_labels.label)
    
    # no_bias_tsne = Window(no_bias_data.copy(), no_bias_knn.copy(), real_labels.esp_id, real_labels.label, index)
    
    plt.axis('off')
    plt.show()

    i += 1
