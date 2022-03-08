import matplotlib.pyplot as plt
import numpy as np
import os

locations = {
    'here': '.',
    'pipeline': r'..\implementations\pipeline'
}

if __name__ == '__main__':
    data = np.loadtxt(open(os.path.join(locations['here'], "all_comps_by_agc_enum.csv"), "rb"), delimiter=",", skiprows=1)
    plt.imshow(data, cmap='hot', interpolation='nearest')
    plt.show()
