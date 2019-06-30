import matplotlib.pyplot as plt
import numpy as np


# Plot result from db
def plot_results_x_string(results, title, percentage=False):
    x_axis = []
    y_axis = []
    # Get data from result of db request
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
    # If x is in ints don't let interpolation of dots
    try:
        int(x[0])
        plt.xticks(x)
    except Exception as ex:
        pass
    plt.bar(x, y)
    # If percentage flag is set and y is numbers, add percentages above every bar
    if percentage:
        try:
            percentage_arr = []
            all_summ = sum(y_axis)
            for y_val in y_axis:
                percentage_arr.append("{0:.2f}".format((y_val/all_summ) * 100) + "%")
            for i in range(len(percentage_arr)):
                plt.text(x=x[i], y=y[i]+0.1, s=percentage_arr[i], size=10)
        except:
            pass
    # Plot result
    plt.show()
