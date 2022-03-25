import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

locations = {
    'here': '.',
    'tests': r'..\timing_test',
}

where = 'tests'

if __name__ == '__main__':
    files = list(filter(lambda f: '.csv' == f[-4:], os.listdir(locations[where])))
    print(f'Opening: {", ".join(files)}')
    plots = []

    for i, file in enumerate(files):
        fig, ax = plt.subplots()
        data = pd.read_csv(os.path.join(locations[where], file))

        # hide axes
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')

        table = ax.table(cellText=data.values, colLabels=data.columns)
        table.auto_set_font_size(False)
        table.set_fontsize(18)

        fig.tight_layout()
    plt.show()
