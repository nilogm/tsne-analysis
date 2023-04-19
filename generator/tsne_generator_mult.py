import pandas as pd
from openTSNE import TSNE

real_labels = pd.read_csv(
    "C:/Users/nilox/OneDrive/NINFA/Dataset/features_all.csv",
    sep=";",
    index_col="id",
    usecols=["id", "label", "esp_id"],
)
label_dict = {
    "Normal": 0,
    "Rubbing": 1,
    "Faulty sensor": 2,
    "Misalignment": 3,
    "Unbalance": 4,
}
labels = real_labels["label"].map(label_dict)

"""

    O arquivo final vai ter:
        index - esp - label - (pred_label - x - y) * número de epochs coletadas
    
"""


def make_TSNE(path, esp, files, out_path):
    # Pega os predicts finais
    base_path = files[-1]
    base_tsne_data = pd.read_csv(path + base_path, sep=",", index_col="id")

    # Mas seleciona somente os itens de treino
    train_idx = real_labels[real_labels["esp_id"] != int(esp)].index
    train_data = base_tsne_data.loc[train_idx.values]

    X_train = train_data[["1", "2", "3", "4", "5", "6", "7", "8"]].to_numpy()

    # Faz o TSNE com base nesses itens
    main_tsne = TSNE(n_jobs=15, verbose=True)
    embedding_train = main_tsne.fit(X_train)

    # Cria as primeiras colunas do DataFrame
    main_data = pd.DataFrame()
    main_data["index"] = base_tsne_data.index.values
    main_data = main_data.set_index("index")
    main_data["esp"] = real_labels.loc[main_data.index.values, "esp_id"]
    main_data["label"] = real_labels.loc[main_data.index.values, "label"]

    # Circula por todos os predicts com epochs para fazer o TSNE
    for f in files[:-1]:
        info = f.split("_")
        epoch = info[-3]

        tsne_data = pd.read_csv(path + f, sep=",", index_col="id")
        X = tsne_data[["1", "2", "3", "4", "5", "6", "7", "8"]].to_numpy()
        embedding_new = embedding_train.transform(X)

        main_data["x_" + epoch] = embedding_new[:, 0]
        main_data["y_" + epoch] = embedding_new[:, 1]

    # Faz o TSNE do final
    X = base_tsne_data[["1", "2", "3", "4", "5", "6", "7", "8"]].to_numpy()
    embedding_new = embedding_train.transform(X)

    main_data["p_label"] = base_tsne_data.p_label
    main_data["x"] = embedding_new[:, 0]
    main_data["y"] = embedding_new[:, 1]

    main_data.to_csv(out_path + "tsne_" + esp + ".csv")


"""

    Fazemos o split e colocamos cada path em um dicionário:
        esp : [epoch predicts, final predicts]
    
    Com isso, pegamos os "final predicts" e fazemos o espaço somente com os itens de treino (exclui a esp atual)
    E então, fazemos todos os outros tsne's de acordo com esse
    O arquivo final vai ter:
        index - esp - label - (pred_label - x - y) * número de epochs coletadas

"""
import os

if __name__ == "__main__":
    path = "C:/Users/nilox/tsne-analysis/results/test1/predicts/"
    out_path = "C:/Users/nilox/tsne-analysis/results/test1/tsne/"

    all_data = {str(i): None for i in range(1, 13)}

    # Para cada arquivo lido, quebrar em partes com split e colocar no array da esp
    for file in os.listdir(path):
        esp = file.split("_")[-1]
        esp = esp.removesuffix(".csv")
        all_data.update(
            {esp: [file]} if all_data[esp] == None else {esp: all_data[esp] + [file]}
        )

    for esp, files in all_data.items():
        if files == None:
            continue

        # Vai em cada item do dicionário para encontrar a network usada
        for f in files:
            info = f.split("_")
            if len(info) == 3:
                break

        network = info[-2]

        # Então, deixa somente as de mesma network no dicionário
        same_network = []
        for f in files:
            info = f.split("_")
            if len(info) == 3:
                end_file = f
                continue

            this_network = info[-2]
            if this_network == network:
                same_network.append(f)

        # Ordenamos os itens da epoch 0 até o final
        for current_place, f in enumerate(same_network):
            info = f.split("_")
            epoch = info[-3]

            correct_place = int(epoch) // 50

            temp = same_network[correct_place]
            same_network[correct_place] = f
            same_network[current_place] = temp

        same_network.append(end_file)

        all_data[esp] = same_network

    for esp, item in all_data.items():
        if item != None:
            make_TSNE(path, esp, item, out_path)
