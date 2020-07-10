'''
Implementation of nu_e + 12C -> X + e-

Based on arXiv:nucl-th/9903022, Table V. Following arXiv:1204.4231 (eqn. III.1),
we fit a power series to the tabulated values. Furthermore, we ignore excited
states of the final nucleus, so that the observed energy is eE = eNu - e_thr.

To determine the the differential cross section dSigma/dE (eNu, eE) from the
total cross section, we approximate a DiracDelta function with one that is
2*epsilon wide and 1/(2*epsilon) high, so that the integral is 1.
'''

from sntools.event import Event

e_thr = 17.338 # energy threshold of this reaction (arXiv:nucl-th/0001050, p. 7)
epsilon = 0.001 # for approximating DiracDelta distribution below


'''
generate_event(eNu, direction):
Generate an event with appropriate incoming/outgoing particles.
Input:
    eNu: neutrino energy
    dirx, diry, dirz: direction of outgoing particle (normalized to 1)
Output:
    event object
'''
def generate_event(eNu, dirx, diry, dirz):
    eE = get_eE(eNu, dirz)
    evt = Event(1006012)
    evt.incoming_particles.append([12, eNu, 0, 0, 1]) # incoming nu_e
    evt.incoming_particles.append((6012, 11178, 0, 0, 1)) # carbon nucleus at rest
    evt.outgoing_particles.append([11, eE, dirx, diry, dirz]) # outgoing electron
    return evt


'''
possible_flavors:
which neutrino flavors ("e", "eb", "x", "xb") interact in this channel
'''
possible_flavors = ["e"]


'''
bounds_eNu
List with minimum & maximum energy of incoming neutrino. The minimum energy is
typically given by the threshold energy for the interaction, while the maximum
energy is given by the supernova neutrino flux.
'''
bounds_eNu = [e_thr + 0.8, 100] # 0.8 MeV = Cherenkov threshold of electron


'''
bounds_eE(eNu, *args):
Kinematical bounds for integration over eE.
Input:
    eNu:  neutrino energy (MeV)
    args: [ignore this]
Output:
    list with minimum & maximum allowed energy of outgoing (detected) particle
'''
def bounds_eE(eNu, *args):
    return [get_eE(eNu) - epsilon, get_eE(eNu) + epsilon]


'''
get_eE(eNu, cosT):
Energy of outgoing (detected particle).
Input:
    eNu:  neutrino energy (MeV)
    cosT: cosine of the angle between neutrino and outgoing (detected) particle
Output:
    one floating point number
'''
def get_eE(eNu, cosT=0):
    return eNu - e_thr


'''
dSigma_dE(eNu, eE):
Differential cross section.
Input:
    eNu: neutrino energy
    eE:  energy of outgoing (detected) particle
Output:
    one floating point number
'''
def dSigma_dE(eNu, eE):
    if abs(get_eE(eNu) - eE) > epsilon:
        # This should never happen, since we set bounds_eE() accordingly above
        # ... but just in case:
        return 0

    sigma0 = 3.439E-44 * (5.067731E10)**2 # convert cm^2 to MeV^-2, see http://www.wolframalpha.com/input/?i=cm%2F(hbar+*+c)+in+MeV%5E(-1)
    a1, a2, a3 = 10.164, -0.4666, 0.0546
    sigma = sigma0 * (a1*(eNu-e_thr) + a2*(eNu-e_thr)**2 + a3*(eNu-e_thr)**3)
    return sigma / (2*epsilon) # Ensure that integration over eE yields sigma


'''
dSigma_dCosT(eNu, cosT):
Distribution of the angle at which the outgoing (detected) particle is emitted.
Input:
    eNu:  neutrino energy (MeV)
    cosT: cosine of the angle between neutrino and outgoing (detected) particle
Output:
    one floating point number
'''
def dSigma_dCosT(eNu, cosT):
    # Small values of cosT are preferred, see arXiv:hep-ex/0105068 (fig. 12,14).
    # However, energy dependence is unclear, so we use a constant value for now.
    if abs(cosT) > 1:
        return 0
    return 0.5


# minimum/maximum neutrino energy that can produce a given positron energy
def _bounds_eNu(eE):
    return (eE + e_thr - epsilon, eE + e_thr + epsilon)