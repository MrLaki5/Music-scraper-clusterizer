import matplotlib.pyplot as plt
import numpy as np


def plot_results_x_string(results, title):
    x_axis = []
    y_axis = []
    for item in results:
        temp_flag = True
        for item_2 in item:
            if temp_flag:
                y_axis.append(item_2)
                temp_flag = False
            else:
                x_axis.append(item_2)

    x = np.array(x_axis)
    y = np.array(y_axis)
    plt.title(title)
    plt.bar(x, y)
    plt.show()
