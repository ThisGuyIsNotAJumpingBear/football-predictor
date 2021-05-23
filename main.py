"""CSC111 Project: main function
"""
import csc111project_data_loading
import csc111project_predictor
import numpy as np
import matplotlib.pyplot as plt
import pprint


def avg(lst: list) -> float:
    """return the average of a list.

    Preconditions:
     - all items in lst are ins or floats.
    """
    return sum(lst) / len(lst)


def plot(lst: list) -> None:
    """Display the graph using the given data.
    """
    n = 10
    X = np.arange(n)

    # each item is decreased by 0.5 because that makes the differences
    # between the predictors clearer.
    Y1 = np.array([sublist[0]-0.5 for sublist in lst])
    Y2 = np.array([sublist[1]-0.5 for sublist in lst])

    plt.axes([0.05, 0.05, 0.9, 0.9])
    plt.bar(X, +Y1, facecolor='#9999ff', edgecolor='white')
    plt.bar(X, -Y2, facecolor='#ff9999', edgecolor='white')

    for x, y in zip(X, Y1):
        plt.text(x + 0.05, y + 0.05, '%.2f' % (y + 0.5), ha='center', va='bottom')
        plt.text(x + 0.05, 0, '%.2f' % (x / 10), ha='center', va='center')

    for x, y in zip(X, Y2):
        plt.text(x + 0.05, -y - 0.05, '%.2f' % (y + 0.5), ha='center', va='top')

    plt.xlim(-0.5, n), plt.xticks([])
    plt.ylim(-1., +1.2), plt.yticks([])

    # savefig('../figures/bar_ex.png', dpi=48)
    plt.show()


str = 'Laliga_full_data.csv'
all_data = csc111project_data_loading.read_file(str)

all_res = []
for i in range(1, 11):
    weight = i / 10
    # initialize 4 predictors
    classic_predictor = csc111project_predictor.Predictor(weight)
    active_predictor = csc111project_predictor.activePredictor(weight)
    random_predictor = csc111project_predictor.randomPredictor(weight)
    normal_predictor = csc111project_predictor.normalPredictor(weight)

    # feed the data one by one
    predictor_list = [classic_predictor, active_predictor, random_predictor, normal_predictor]
    for count, item in enumerate(predictor_list):
        for row in all_data:
            item.feed_data(row)

    # get the seasonal accuracy result and their relative performance
    res = [item.get_seasonal_accuracy()[-1] for item in predictor_list]
    # res = [avg(item.get_seasonal_accuracy()) for item in predictor_list]
    performance = [avg([res[0] / res[2], res[0] / res[3]]),
                   avg([res[1] / res[2], res[1] / res[3]])]
    all_res.append(performance)

plot(all_res)
