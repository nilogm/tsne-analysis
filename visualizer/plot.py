import matplotlib as mpl
import pandas as pd
import numpy as np

# data_path = "/home/ngmonteiro/RPDBCS"
data_path = "C:/Users/nilox/OneDrive/NINFA/Dataset"

# mpl.use('TkAgg')

NORM_FREQ = 37.28941975

df = pd.read_csv('%s/features_all.csv' % data_path, delimiter=';')
df2 = pd.read_csv('%s/labels.csv' % data_path, delimiter=';', comment='#')

with np.load('%s/spectrum.npz' % data_path) as f:
    mat = [f[str(i.id)][100:6200] for _, i in df.iterrows()]

def get_axis(index):
    Y_index = df[df['id'] == index].index.values[0]
    Y = mat[Y_index]

    entry = df2.iloc[Y_index]
    factor = min(NORM_FREQ / entry.real_rotation_hz, 1.0)
    X = np.arange(Y.size + 100) * (entry.xhz_step / factor) + (entry.xhz_0 / factor)
    X = X[100:] / entry.real_rotation_hz

    return X, Y
