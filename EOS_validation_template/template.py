from math import exp, log

class EquationState(object):
    def  __init__(self,*,n,t,d,l,eta,beta,gamma,epsilon,Tc,rhoc,a1,a2,c0,u,v,Nterms=(5,5,6)):
        assert(sum([abs(len(v)-len(n)) for v in(n,t,d,l,eta,beta,gamma,epsilon)])==0)
        self.n=n
        self.t=t
        self.d=d
        self.l=l
        self.eta=eta
        self.beta=beta
        self.gamma=gamma
        self.epsilon=epsilon
        self.Tc=Tc
        self.rhoc=rhoc
        self.a1 = a1
        self.a2 = a2
        self.c0 = c0
        self.u = u
        self.v = v
        self.Npoly, self.Nexp, self.Ngauss = Nterms
    def resid_derivs(self,T,rho):
        tau = self.Tc/T
        delta = rho/self.rhoc
        # Initialize variables
        A00, A10, A01, A20, A11, A02 = 0,0,0,0,0,0
        for i in range(0,self.Npoly):
            _s = self.n[i]*delta**self.d[i]*tau**self.t[i]
            A00 += _s
            A10 += self.t[i]*_s
            A01 += self.d[i]*_s
            A20 += self.t[i]*(self.t[i]-1)*_s
            A11 += self.d[i]*self.t[i]*_s
            A02 += self.d[i]*(self.d[i]-1)*_s
        for i in range(self.Npoly,self.Npoly+self.Nexp):
            _s = self.n[i]*delta**self.d[i]*tau**self.t[i]*exp(-delta**self.l[i])
            A00 += _s
            A10 += _s*self.t[i]
            A01 += _s*(self.d[i]-self.l[i]*delta**self.l[i])
            A20 += _s*self.t[i]*(self.t[i]-1)
            A11 += _s*self.t[i]*(self.d[i]-self.l[i]*delta**self.l[i])
            A02 += _s*((self.d[i]-self.l[i]*delta**self.l[i])*(self.d[i]-1-self.l[i]*delta**self.l[i])-self.l[i]**2*delta**self.l[i])

        for i in range(self.Npoly+self.Nexp, self.Npoly+self.Nexp+self.Ngauss):
            _s = self.n[i]*delta**self.d[i]*tau**self.t[i]*exp(-self.eta[i]*(delta-self.epsilon[i])**2-self.beta[i]*(tau-self.gamma[i])**2)
            A00 += _s
            A10 += _s*(self.t[i]-2*self.beta[i]*tau*(tau-self.gamma[i]))
            A01 += _s*(self.d[i]-2*self.eta[i]*delta*(delta-self.epsilon[i]))
            A20 += _s*((self.t[i]-2*self.beta[i]*tau*(tau-self.gamma[i]))**2-self.t[i]-2*self.beta[i]*tau**2)
            A11 += _s*(self.t[i]-2*self.beta[i]*tau*(tau-self.gamma[i]))*(self.d[i]-2*self.eta[i]*delta*(delta-self.epsilon[i]))
            A02 += _s*((self.d[i]-2*self.eta[i]*delta*(delta-self.epsilon[i]))**2-self.d[i]-2*self.eta[i]*delta**2)
        return A00,A10,A01,A20,A11,A02

    def ideal_derivs(self, T, rho):
        tau = self.Tc/T
        delta = rho/self.rhoc
        A01 = 1
        A02 = -1
        A11 = 0
        A00 = ((0 if delta==0 else log(delta)) + self.a1 + self.a2*tau + (self.c0-1)*log(tau)
        + sum([
        v_i*log(1-exp(-u_i*tau/self.Tc)) for u_i, v_i in zip(self.u, self.v)
        ]))
        A10 = (self.a2*tau + (self.c0-1) + tau*sum([
            v_i*(u_i/self.Tc)/(exp(u_i*tau/self.Tc)-1) for u_i, v_i in zip(self.u, self.v)
        ]))
        A20 = (-(self.c0-1) - tau**2*sum([
            v_i*(u_i/self.Tc)**2*exp(u_i*tau/self.Tc)/(exp(u_i*tau/self.Tc)-1)**2 for u_i,
            v_i in zip(self.u, self.v)
        ]))
        return A00, A10, A01, A20, A11, A02

    def derivs(self, T, rho):
        return [resid+ideal for resid,ideal in zip(self.resid_derivs(T,rho),self.ideal_derivs(T,rho))]

def fmt(*inputs):
    fmts = ['{0:<10.0f}','{0:<10.2g}','{0:<10.7g}','{0:<10.6g}','{0:<10.6g}','{0:<10.6g}']
    return ' '.join([fmt.format(inp) for fmt, inp in zip(fmts, inputs)])

def test_R1234zeZ():
    n = [0.03194509, 1.394592 ,-2.300799 ,-0.2556693 , 0.1282934 ,-1.335381 ,-1.366494 ,
        0.2004912 ,-0.6489709 ,-0.02220033, 1.66538 , 0.3427048 ,-0.6510217 ,-0.5067066 ,
        -0.1231787 , 0.08828106]
    t = [1.0 ,0.333,1.0 ,1.0 ,0.38 ,2.85 ,3.16 ,0.607,2.2 ,1.0 ,1.83 ,3.3 ,1.9 ,2.6 ,2.9 , 3.0 ]
    d = [4,1,1,2,3,1,3,2,2,7,1,1,3,2,3,2]
    l = [0]*5+[2,2,1,2,1]+[0]*6
    eta = [0]*10+[1.108,1.579,1.098,0.672,3.38 ,1.6 ]
    beta = [0]*10+[0.563,1.724,0.806,0.505,26.4 ,8.82 ]
    gamma = [0]*10+[1.246,1.05 ,1.0 ,0.677,1.302,1.274]
    epsilon = [0]*10+[0.933,0.786,0.496,0.327,0.523,0.308]
    EOS = EquationState(n=n,t=t,d=d,l=l,eta=eta,beta=beta,gamma=gamma,epsilon=epsilon,
        Tc=423.27,rhoc=4000,a1=-2.422442259,a2=8.190539844,c0=4,v=[4.2365,13.063],u=[20,1335],Nterms=(5,5,6))
    for T,rho in [(300,0),(300,11),(300,0.05),(400,8),(400,1),(424,4)]:
        rho = rho*1000
        R = 8.3144598
        Ar00,Ar10,Ar01,Ar20,Ar11,Ar02 = EOS.resid_derivs(T,rho)
        A00,A10,A01,A20,A11,A02 = EOS.derivs(T,rho)
        p = rho*R*T*(Ar01+1)
        cv = -R*A20
        cp = cv + R*(1+Ar01-Ar11)**2/(1+2*Ar01+Ar02)
        M = 114.0416/1000
        w = (R*T/M*((1+2*Ar01+Ar02)-(1+Ar01-Ar11)**2/(A20)))**0.5
        print(fmt(T,rho/1000, p/1e6, cv/1e3, cp/1e3, w))

if __name__ == '__main__':
    test_R1234zeZ()

"""
Running this script should yield:
300        0          0          0.0858698  0.0941842  154.887   
300        11         10.99498   0.100637   0.14158    704.695   
300        0.05       0.1189126  0.0883387  0.0991296  149.222   
400        8          5.085752   0.119956   0.191425   302.189   
400        1          2.115059   0.121      0.181      121.387   
424        4          3.578101   0.14516    10.1999    82.916  
"""