"""
Plot wood conversion and gas, tar, gas+char yields from primary and secondary
reactions as determined by the Liden 1988 kinetic scheme for biomass pyrolysis.
Note that this scheme only provides overall wood conversion (K) and the
secondary reaction of tar to gas (K2). Other rate constants calculated from
maximum theoretical tar yield.

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

def liden(wood, gas1, tar, gaschar, T, dt, s=1):
    """
    Primary and secondary kinetic reactions from Liden 1988 paper. Parameters
    for total wood converstion (K = K1+K3) and secondary tar conversion (K2) are
    the only ones provided in paper. Can calculate K1 and K3 from phistar.

    Parameters
    ----------
    wood = wood concentration, kg/m^3
    gas1 = gas concentration from tar -> gas, kg/m^3
    tar = tar concentation, kg/m^3
    gaschar = (gas+char) concentration, kg/m^3
    T = temperature, K
    dt = time step, s
    s = 1 primary reactions only, 2 primary and secondary reactions

    Returns
    -------
    nwood = new wood concentration, kg/m^3
    ngas1 = new gas concentration, kg/m^3
    ntar = new tar concentration, kg/m^3
    ngaschar = new (gas+char) concentration, kg/m^3
    """
    # A = pre-factor (1/s) and E = activation energy (kJ/mol)
    A = 1.0e13;         E = 183.3     # wood -> tar and (gas + char)
    A2 = 4.28e6;        E2 = 107.5    # tar -> gas
    R = 0.008314        # universal gas constant, kJ/mol*K
    phistar = 0.703     # maximum theoretical tar yield, (-)

    # reaction rate constant for each reaction, 1/s
    K = A * np.exp(-E / (R * T))        # wood -> tar and (gas + char)
    K1 = K * phistar                    # from phistar = K1/K
    K2 = A2 * np.exp(-E2 / (R * T))     # tar -> gas
    K3 = K - K1                         # from K = K1 + K3

    if s == 1:
        # primary reactions only
        rw = -K*wood        # wood rate]
        rt = K1*wood        # tar rate
        rgc = K3*wood       # (gas+char) rate
        nwood = wood + rw*dt            # update wood concentration
        ngas1 = 0                       # no gas yield from primary reactions
        ntar = tar + rt*dt              # update tar concentration
        ngaschar = gaschar + rgc*dt     # update (gas+char) concentration
    elif s == 2:
        # primary and secondary reactions
        rw = -K*wood            # wood rate
        rg = K2*tar             # gas rate
        rt = K1*wood - K2*tar   # tar rate
        rgc = K3*wood           # (gas+char) rate
        nwood = wood + rw*dt            # update wood concentration
        ngas1 = gas1 + rg*dt            # update gas concentration
        ntar = tar + rt*dt              # update tar concentration
        ngaschar = gaschar + rgc*dt     # update (gas+char) concentration

    # return new wood, gas, tar, (gas+char) mass concentrations, kg/m^3
    return nwood, ngas1, ntar, ngaschar 


def liden2(wood, gas1, tar, gaschar, gas, char, T, dt):
    """
    Primary and secondary kinetic reactions from Liden 1988 paper. Parameters
    for total wood converstion (K = K1+K3) and secondary tar conversion (K2) are
    the only ones provided in paper. Can calculate K1 and K3 from phistar.

    Parameters
    ----------
    wood = wood concentration, kg/m^3
    gas1 = gas concentration from tar -> gas, kg/m^3
    tar = tar concentation, kg/m^3
    gaschar = (gas+char) concentration, kg/m^3
    gas = gas concentration from tar -> gas and gaschar, kg/m^3
    char = char concentration from gaschar, kg/m^3
    T = temperature, K
    dt = time step, s

    Returns
    -------
    nwood = new wood concentration, kg/m^3
    ngas1 = new gas1 concentration, kg/m^3
    ntar = new tar concentration, kg/m^3
    ngaschar = new (gas+char) concentration, kg/m^3
    ngas = new gas concentration, kg/m^3
    nchar = new char concentration, kg/m^3
    """
    # A = pre-factor (1/s) and E = activation energy (kJ/mol)
    A = 1.0e13;         E = 183.3     # wood -> tar and (gas + char)
    A2 = 4.28e6;        E2 = 107.5    # tar -> gas
    R = 0.008314        # universal gas constant, kJ/mol*K
    phistar = 0.703     # maximum theoretical tar yield, (-)

    # reaction rate constant for each reaction, 1/s
    K = A * np.exp(-E / (R * T))        # wood -> tar and (gas + char)
    K1 = K * phistar                    # from phistar = K1/K
    K2 = A2 * np.exp(-E2 / (R * T))     # tar -> gas
    K3 = K - K1                         # from K = K1 + K3
    
    # assume a fixed carbon to estimate individual char and gas yields
    FC = 0.14               # weight fraction of fixed carbon in wood, (-)
    c3 = FC/(1-phistar)     # char fraction of wood, (-)
    g3 = 1-c3               # gas fraction of wood, (-)
    
    # primary and secondary reactions
    rw = -K*wood            # wood rate
    rg = K2*tar             # gas rate
    rt = K1*wood - K2*tar   # tar rate
    rgc = K3*wood           # (gas+char) rate
    nwood = wood + rw*dt            # update wood concentration
    ngas1 = gas1 + rg*dt            # update gas concentration
    ntar = tar + rt*dt              # update tar concentration
    ngaschar = gaschar + rgc*dt     # update (gas+char) concentration
    ngas = ngas1 + g3*ngaschar      # update total gas concentration
    nchar = c3*ngaschar             # update char conentration

    return nwood, ngas1, ntar, ngaschar, ngas, nchar


# Products from Kinetic Scheme
# ------------------------------------------------------------------------------

# store concentrations from reactions at each time step, concentrations reported
# on a mass basis as kg/m^3 or mass fraction, row 1 for primary reactions and
# row 2 for primary+secondary reactions
wood = np.ones((3, nt))         # wood concentration vector
gas1 = np.zeros((3, nt))        # gas concentration vector
tar = np.zeros((3, nt))         # tar concentration vector
gaschar = np.zeros((3, nt))     # (gas+char) concentration vector
gas = np.zeros(nt)              # total gas concentration vector
char = np.zeros(nt)             # char concentration vector

# products from primary reactions and primary+secondary reactions
for i in range(1, nt):
    wood[0, i], gas1[0, i], tar[0, i], gaschar[0, i] = liden(wood[0, i-1], gas1[0, i-1], tar[0, i-1], gaschar[0, i-1], T, dt)
    wood[1, i], gas1[1, i], tar[1, i], gaschar[1, i] = liden(wood[1, i-1], gas1[1, i-1], tar[1, i-1], gaschar[1, i-1], T, dt, s=2)
    wood[2, i], gas1[2, i], tar[2, i], gaschar[2, i], gas[i], char[i] = liden2(wood[2, i-1], gas1[2, i-1], tar[2, i-1], gaschar[2, i-1], gas[i-1], char[i-1], T, dt)

# Print Mass Balance
# ------------------------------------------------------------------------------

# check mass balance at each time step which should equal 1
print('total mass fraction (primary, gaschar) \n', wood[0]+gas1[0]+tar[0]+gaschar[0])
print('total mass fraction (pri+sec, gaschar) \n', wood[1]+gas1[1]+tar[1]+gaschar[1])
print('total mass fraction (pri+sec, gas and char) \n', wood[2]+tar[2]+gas+char)

# Plot Results
# ------------------------------------------------------------------------------

py.ion()
py.close('all')

py.figure(1)
py.plot(t, wood[0], lw=2, label='wood')
py.plot(t, gas1[0], lw=2, label='gas1')
py.plot(t, tar[0], lw=2, label='tar')
py.plot(t, gaschar[0], lw=2, label='gas+char')
py.title('Liden 1988 primary reactions at T = {} K'.format(T))
py.xlabel('Time (s)')
py.ylabel('Concentration (mass fraction)')
py.legend(loc='best', numpoints=1, frameon=False)
py.grid()

py.figure(2)
py.plot(t, wood[1], lw=2, label='wood')
py.plot(t, gas1[1], lw=2, label='gas1')
py.plot(t, tar[1], lw=2, label='tar')
py.plot(t, gaschar[1], lw=2, label='gas+char')
py.title('Liden 1988 primary and secondary reactions at T = {} K'.format(T))
py.xlabel('Time (s)')
py.ylabel('Concentration (mass fraction)')
py.legend(loc='best', numpoints=1, frameon=False)
py.grid()

py.figure(3)
py.plot(t, wood[2], lw=2, label='wood')
py.plot(t, gas, lw=2, label='gas')
py.plot(t, tar[2], lw=2, label='tar')
py.plot(t, char, lw=2, label='char')
py.title('Liden 1988 primary and secondary reactions at T = {} K'.format(T))
py.xlabel('Time (s)')
py.ylabel('Concentration (mass fraction)')
py.legend(loc='best', numpoints=1, frameon=False)
py.grid()

