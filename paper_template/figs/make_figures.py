import numpy as np
import matplotlib.pyplot as plt
plt.style.use('classic')
plt.style.use('mystyle.mplstyle')

def make_figure_hot():
    x = [1,2,3]
    y = np.sin(x)
    plt.plot(x, y, color='r')
    plt.tight_layout(pad=0.2)
    plt.savefig('hot.pdf')

def make_figure_cold():
    x = [1,2,3]
    y = np.cos(x)
    plt.plot(x, y,color='c')
    plt.tight_layout(pad=0.2)
    plt.savefig('cold.pdf')

if __name__ == '__main__':

    # ************* Main manuscript *********************
    make_figure_hot()

    # **************** SI ******************
    make_figure_cold()