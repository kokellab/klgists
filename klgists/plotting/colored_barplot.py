import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple

def colored_barplot(x: np.ndarray, y: np.ndarray, colors: np.ndarray, y_ticks: Optional[np.ndarray]=None, fig_size: Tuple[float, float]=(10.0, 10.0), label_rotation: float=75):
    index = np.arange(0, len(x))
    fig = plt.figure()
    fig.set_size_inches(fig_size)
    ax = fig.add_subplot(111)
    plot = ax.bar(index, y, color=colors, align='center')
    ax.set_xticks(index)
    ax.autoscale()  # otherwise there's whitespace on the rhs
    if y_ticks is not None:
        ax.set_yticks(y_ticks)
    ax.set_xticklabels(x, rotation=label_rotation)
    return plot
