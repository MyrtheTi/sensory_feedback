"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-03-07 15:50:32
 * @desc Script to plot the results from the validation
"""

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score

from utils import read_file


def plot_confusion_matrix(path):
    """ Plots the confusion matrices of the validation using all levels and
    when separated in 3 levels (flexion, co-contraction, and extension).

    Args:
        path (string): Path of the validation files.
    """
    true_labels = read_file(path, 'true_labels.csv', ['int'])[0]
    predicted_labels = read_file(path, 'predicted_labels.csv', ['int'])[0]

    fig, axes = plt.subplots(ncols=2, figsize=(20, 10))
    titles_options = [
        ("Confusion matrix with all levels", true_labels, predicted_labels,
         None),
        ("Confusion matrix with combined levels", converge_levels(true_labels),
         converge_levels(predicted_labels),
         ['flexion', 'co-contraction', 'extension'])
    ]

    for (title, true, predicted, labels), ax in zip(
            titles_options, axes.flatten()):
        ConfusionMatrixDisplay.from_predictions(
            true,
            predicted,
            cmap=plt.cm.Blues,
            normalize='true',
            ax=ax,
            display_labels=labels
        )
        ax.set_title(title)
        accuracy = accuracy_score(true, predicted)

        ax.set_ylabel('True level')
        ax.set_xlabel(f'Predicted level\naccuracy={accuracy:0.4f}')
    plt.tight_layout()
    plt.show()


def converge_levels(labels):
    """ Converges the labels of the predicted and true levels to 3 classes:
    flexion, co-contraction, and extension.

    Args:
        labels (list): list with predicted or true levels.

    Returns:
        list: list with string class for each level
    """
    converged = []
    for level in labels:
        if level < 0:
            converged.append('flexion')
        if level > 0:
            converged.append('extension')
        if level == 0:
            converged.append('co-contraction')
    return converged


if __name__ == '__main__':
    user = 'me'
    date = '2023_03_02'

    path = 'user_files/' + user + '/' + date + '/'
    print(path)
    plot_confusion_matrix(path)
