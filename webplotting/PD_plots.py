import timeit
import json

# https://stackoverflow.com/questions/43356795/can-the-webagg-backend-for-matplotlib-work-with-my-django-site
import matplotlib as mpl
mpl.use('webagg')

# import plotly
# from plotly.offline import init_notebook_mode, plot_mpl

import matplotlib.pyplot as plt
import numpy as np

from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
root = 'c:/Program Files (x86)/REFPROP'
RP = REFPROPFunctionLibrary(root)
RP.SETPATHdll(root)

def get_PD_data(fluids, Temps, pmax,  rhomin, Npts):
    RP.SETFLUIDSdll(fluids)

    Tt = RP.REFPROPdll("", "TRIP", "T", RP.MOLAR_BASE_SI, 0,0,0,0,[1.0]).Output[0]
    Tc = RP.REFPROPdll("", "CRIT", "T", RP.MOLAR_BASE_SI, 0,0,0,0,[1.0]).Output[0]
    Dmax = RP.REFPROPdll("", "TRIP", "D", RP.MOLAR_BASE_SI, 0,0,0,0,[1.0]).Output[0]

    curves = []

    def make_isotherm(T, rhovec):
        vals = []
        for rho in rhovec:
            r = RP.REFPROPdll("", "TD", "P", RP.MOLAR_BASE_SI, 0,0,T,rho,[1.0])
            vals.append(r.Output[0] if r.ierr == 0 else np.nan)
        return vals

    # Vapor-liquid equilibrium
    for Q in [0, 1]:
        Tvec = np.linspace(Tt, Tc, Npts)
        rhovec,pvec = [],[]
        for T in Tvec:
            rho,p = RP.REFPROPdll("", "QT", "D;P", RP.MOLAR_BASE_SI, 0, 0, Q, T, [1.0]).Output[0:2]
            rhovec.append(rho)
            pvec.append(p)
        curves.append({
            'segments': [
                {
                'x': rhovec,
                'y': pvec,
                'color': 'k'
                }
            ]
        })

    # Isotherms
    for T in Temps:
        # If supercritical, then you have one piece
        if T > Tc:
            rhovec = np.geomspace(rhomin, Dmax, Npts)
            curves.append({
                'segments': [
                    {
                    'x': rhovec.tolist(),
                    'y': make_isotherm(T, rhovec),
                    'color': 'r'
                    }
                ]
                })
        else:
            r = RP.REFPROPdll("", "QT", "DLIQ;DVAP", RP.MOLAR_BASE_SI, 0, 0, 0, T, [1.0])
            rholiq, rhovap = r.Output[0:2]
            for rhochunk in [np.geomspace(rhomin, rhovap, Npts), np.geomspace(rholiq, Dmax, Npts)]:
                curves.append({
                    'segments': [
                        {
                        'x': rhochunk.tolist(),
                        'y': make_isotherm(T, rhochunk),
                        'color': 'b'
                        }
                    ]
                    })
    return curves

def plot_it(curves, *, show, plotlyfilename):
    """ 
    params:
        show: True to call plt.show(), closed otherwise
        plotlyfilename: If a plotly filename is provided, use it to generate a plotly figure (seems to be broken...)
    """
    fig, ax = plt.subplots(1,1)
    for curve in curves:
        for segment in curve['segments']:
            plt.plot(segment['x'], segment['y'], segment['color'])
    plt.yscale('log')
    plt.gca().set(xlabel=r'$\rho$ / mol/m$^3$', ylabel='$p$ / Pa')
    plt.tight_layout(pad=0.2)

    # if plotlyfilename:
    #     plot_mpl(plt.gcf(), filename=plotlyfilename)

    if show:
        plt.show()
    else:
        plt.close('all')

if __name__ == '__main__':
    Npts = 1000
    tic = timeit.default_timer()
    data = get_PD_data(fluids='Argon', Temps = [80,90,100,120,130,140,150,160,180,300], pmax=1e10, Npts=Npts, rhomin=1e-5)
    with open(f'PDdata_N{Npts}.json','w') as fp:
        fp.write(json.dumps(data, indent=2))
    toc1 = timeit.default_timer()
    plot_it(data, show=True, plotlyfilename=f"PDplot_N{Npts}")
    toc2 = timeit.default_timer()

    print(toc1-tic, 'sec. to build')
    print(toc2-toc1, 'sec. to plot')