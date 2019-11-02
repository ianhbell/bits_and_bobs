import sys
import json

import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt

class Problem:
    def __init__(self, *, x, y, Nnum, Nden):
        self.x=x
        self.yinput=y
        self.Nnum=Nnum
        self.Nden=Nden

    def eval_RHS(self,*, x, cnum, cden):
        # cnum and cden are in increasing order, but polyval wants decreasing order
        # cden is from degree 1 and up
        return np.polyval(cnum[::-1], x)/(1+np.polyval(cden[::-1].tolist()+[0], x))

    def decompose(self, c):
        assert(len(c) == self.Nnum+self.Nden)
        cnum = c[0:self.Nnum]
        cden = c[self.Nnum::]
        return cnum, cden

    def objective(self, c):
        cnum, cden = self.decompose(c)
        yeval = self.eval_RHS(x=self.x, cnum=cnum, cden=cden)
        return ((yeval-self.yinput)**2).sum()

    def do_fit(self, *, bounds=None):
        res = scipy.optimize.differential_evolution(
            self.objective, 
            bounds=[(-10,10)]*(self.Nnum+self.Nden), 
            disp=True
            )
        return res.x

    def plot_model(self, c):
        plt.plot(self.x, self.yinput, 'o')
        cnum, cden = self.decompose(c)
        plt.plot(self.x, self.eval_RHS(x=self.x, cnum=cnum, cden=cden))
        plt.show()

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Fit a rational polynomial function to 1D data')
    parser.add_argument('--filename', type=str, required=True, nargs=1, help='The input filename in JSON format with fields x and y')
    parser.add_argument('--Nnum', type=int, required=True, nargs=1, help='The degree of the summation in the numerator')
    parser.add_argument('--Nden', type=int, required=True, nargs=1, help='The degree of the denominator')

    args = parser.parse_args() # The version for "production"
    #args = parser.parse_args(['--filename','fit_data.json', '--Nnum', '5', '--Nden', '5'])  # For testing
    with open(args.filename[0]) as fp:
        j = json.load(fp)
        p = Problem(x=j['x'], y=j['y'], Nnum=args.Nnum[0], Nden=args.Nden[0])
        c = p.do_fit()
        p.plot_model(c)