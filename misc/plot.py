import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt(open("all_comps_by_agc_enum.csv", "rb"), delimiter=",", skiprows=1)
plt.imshow(data, cmap='hot', interpolation='nearest')
plt.show()
