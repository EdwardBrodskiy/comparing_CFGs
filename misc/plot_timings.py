import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

locations = {
    'here': '.',
    'tests': r'..\timing_test\results',
}

where = 'tests'

if __name__ == '__main__':
    files = list(filter(lambda f: '.csv' == f[-4:], os.listdir(locations[where])))
    print(f'Opening: {", ".join(files)}')
    plots = []
    for i, file in enumerate(files):
        data = pd.read_csv(os.path.join(locations[where], file), header=None)
        data[0] = data[0].astype(dtype='category')
        data = data.T
        data.columns = data.iloc[0]
        data = data[1:]

        plt.figure(i, figsize=(10, 10))
        data.plot()
        plt.title(file[:-4])
    plt.show()
