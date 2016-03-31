"""
Plot wood conversion as determined by the Liden 1988 kinetic scheme for biomass
pyrolysis. Note that this scheme only provides overall wood conversion and the
secondary reaction of tar to gas.

Reference:
Liden, Berruti, Scott, 1988. Chem. Eng. Comm., 65, pp 207-221.
"""

import numpy as np
import matplotlib.pyplot as py

# Parameters
# ------------------------------------------------------------------------------

T = 773  # temperature for rate constants, K

dt = 0.01                               # time step, delta t
tmax = 25                               # max time, s
t = np.linspace(0, tmax, num=tmax/dt)   # time vector
nt = len(t)                             # total number of time steps

# Function for Liden 1988 Kinetic Scheme
# ------------------------------------------------------------------------------

def liden(wood, tar, T, dt, s=1):
    """
    Primary and secondary kinetic reactions from Liden 1988 paper. Parameters
    only for total wood converstion and secondary tar conversion are given.

    Parameters
    ----------
    wood = wood concentration, kg/m^3
    tar = tar concentation, kg/m^3
    T = temperature, K
    dt = time step, s
    s = 1 primary reactions only, 2 primary and secondary reactions

    Returns
    -------
    nwood = new wood concentration, kg/m^3
    ngas = new gas concentration, kg/m^3
    ntar = new tar concentration, kg/m^3
    nchar = new char concentration, kg/m^3
    """
    # A = pre-factor (1/s) and E = activation energy (kJ/mol)
    A = 1.0e13;         E = 183.3     # wood -> tar and (gas + char)
    A2 = 4.28e6;        E2 = 107.5    # tar -> gas
    R = 0.008314        # universal gas constant, kJ/mol*K

    # reaction rate constant for each reaction, 1/s
    K = A * np.exp(-E / (R * T))        # wood -> tar and (gas + char)
    K2 = A2 * np.exp(-E2 / (R * T))     # tar -> gas

    if s == 1:
        # primary reactions only
        rw = -K*wood    # wood rate
        rt = -K2*wood   # tar rate
        nwood = wood + rw*dt    # update wood concentration
        ntar = tar + rt*dt      # update tar concentration
    elif s == 2:
        # primary and secondary reactions
        rw = -K*wood    # wood rate
        rt = -K2*wood   # tar rate
        nwood = wood + rw*dt    # update wood concentration
        ntar = tar + rt*dt      # update tar concentration

    # return new wood, tar mass concentrations, kg/m^3
    return nwood, ntar

# Products from Kinetic Scheme
# ------------------------------------------------------------------------------

# store concentrations from primary reactions at each time step
# concentrations reported on a mass basis as kg/m^2
wood = np.ones(nt)  # wood concentration vector
tar = np.zeros(nt)  # tar concentration vector

# products from primary reactions only
for i in range(1, nt):
    wood[i], tar[i] = liden(wood[i-1], tar[i-1], T, dt)

# Plot Results
# ------------------------------------------------------------------------------

py.ion()
py.close('all')

py.figure(1)
py.plot(t, wood, lw=2, label='wood')
py.title('Liden 1988 primary reactions at T = {} K'.format(T))
py.xlabel('Time (s)')
py.ylabel('Concentration (m.f. basis)')
py.legend(loc='best', numpoints=1)
py.grid()