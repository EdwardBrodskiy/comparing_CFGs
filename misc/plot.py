import matplotlib.pyplot as plt
import numpy as np
import os

locations = {
    'here': '.',
    'pipeline': r'..\implementations\pipeline',
    'analyzers': r'..\implementations\pipeline\analyzers\comparisons'
}

where = 'analyzers'

if __name__ == '__main__':
    files = list(filter(lambda f: '.csv' == f[-4:], os.listdir(locations[where])))
    print(files)
    plots = []
    for i, file in enumerate(files):
        fig, ax = plt.subplots()
        data = np.loadtxt(open(os.path.join(locations[where], file), "rb"), delimiter=",")
        plt.figure(i, figsize=(10, 10))
        plt.imshow(data)
        plt.title(file[:-4])
        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        cax = plt.axes([0.85, 0.1, 0.075, 0.8])
        ax.xaxis.tick_top()
        plt.colorbar(cax=cax)
    plt.show()
