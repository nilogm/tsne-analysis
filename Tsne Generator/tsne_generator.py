import pandas as pd
from os.path import exists
from openTSNE import TSNE


real_labels = pd.read_csv('/home/ngmonteiro/RPDBCS/features_all.csv', sep=';',
                          index_col='id', usecols=['id', 'label', 'esp_id'])
label_dict = {
    'Normal': 0,
    'Rubbing': 1,
    'Faulty sensor': 2,
    'Misalignment': 3,
    'Unbalance': 4
}
labels = real_labels['label'].map(label_dict)


def setDataFrame(x, y, keys, esps, labels, pred_labels, mode):
    data = pd.DataFrame()
    data["x"] = x
    data["y"] = y
    data["index"] = keys
    data["esp"] = esps
    data["labels"] = labels
    data["p_label"] = pred_labels
    data["mode"] = mode

    return data


def make_TSNE(path, pathTest):
    info = pd.read_csv(path, sep=',')
    infoTest = pd.read_csv(pathTest, sep=',')

    X_train = info[['1', '2', '3', '4', '5', '6', '7', '8']].to_numpy()
    X_test = infoTest[['1', '2', '3', '4', '5', '6', '7', '8']].to_numpy()

    tsne = TSNE(n_jobs=15, verbose=True)
    embedding_train = tsne.fit(X_train)
    embedding_test = embedding_train.transform(X_test)

    indices = info.id.tolist()
    data_train = setDataFrame(embedding_train[:, 0], embedding_train[:, 1], indices,
                              real_labels.esp_id[indices].tolist(
    ), labels[indices].tolist(),
        info.p_label.tolist(), ['train' for _ in range(len(indices))])

    indices = infoTest.id.tolist()
    data_test = setDataFrame(embedding_test[:, 0], embedding_test[:, 1], indices,
                             real_labels.esp_id[indices].tolist(
    ), labels[indices].tolist(),
        infoTest.p_label.tolist(), ['test' for _ in range(len(indices))])

    data = pd.concat([data_train, data_test])
    return data


folder = ""
pathStart = "/home/ngmonteiro/ESPset-normal/sibling results/predicts/%s/predict_" % folder

i = 1
while (True):
    path = pathStart + "%d.csv" % i
    pathTest = pathStart + "test_%d.csv" % i

    if (not exists(path)):
        break

    data = make_TSNE(path, pathTest)

    data.to_csv("/home/ngmonteiro/ESPset-normal/results/tsne/%s/tsne_%d.csv" %
                (folder, i), index=False)
    i += 1
