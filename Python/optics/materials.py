""" Functions for evaluating the Sellmeier Equation for a variety of materials. """

import sys
import numpy as np

def sellmeier(*args):
    """ Find wavelength dependence of the refractive index of a given material.
    
    If the function is called without any arguments, a list of available 
    materials with their ranges of validity and a reference is returned.
    
    sellmeier(material,wl) returns a list of indices of refraction evaluated at 
    the wl (specified in um).  Depending on the material, there will be 1, 2 or 3 
    indices of refraction.  If the material is isotropic there is only one index.  
    If it is uniaxial the ordinary index is specified first, and then the extraordinary.  
    If the material is biaxial it goes X,Y then Z."""
    
    # All of the data for the different materials is stored in the following dict.
    # Each element has the key as the material abbreviation, and the value as a 
    # list where the first element is a tuple of tuples, where each value of the    
    # outer tuple is for a given indice, and the values in the inner tuple are 
    # A, B, C, D, E, F, and G in this form of the sellmeier Eqn.:
    # n^2 = A + B*l^2/(l^2 - C) + D*l^2/(l^2 - E) + F*l^2/(l^2 - G)
    # the second value in the list is an ordered pair indicating the range of 
    # validity.  The third value is a string indicating where the value are from.
    materials = {
        'LiNbO':[((2.23920,2.5112,0.047089,7.1333,272.316,0,0),
                  (2.3247,2.2565,0.0441,14.503,671.58,0,0)),
                  (0.4,3.1),
                 'Fundamentals of Photonics, 2e pp 180'],
        'BBO':  [((1.46357,1.26172,0.01628,0.00166,30.,0,0),
                  (1.40567,0.95869,0.01431,0.01644,30.,0,0)),
                  (0.26,1.06),
                  'Applied Optics, vol 28, No 2. 15 Jan 1989 pp 202-203'],
        'NBAF10':[((1,1.5851495,0.00926681282,0.143559385,0.0424489805,1.08521269,105.613573),
            (1,1.5851495,0.00926681282,0.143559385,0.0424489805,1.08521269,105.613573)),
            (0.35, 2.5),
            'RefractiveIndex.info']
            }

    
    if len(args) == 0:
        print('Abbr:\t Range [um]\t Reference')
        for m in materials.keys():
            print(m + ': \t' + str(materials[m][1]) + '\t-- ' + materials[m][2])
        return
    elif len(args) != 2:
        raise ValueError('Must have zero or two arguments.')
    else:
        material = args[0]
        wl = args[1] # the wavelengths where the sellmeier eqn is evaluated
        
    if material not in materials:
        raise ValueError('The first argument must be one of the following \
                          materials: ' + ",".join(materials.keys()))
        
    coef = materials[material][0]
    n = []
    wl2 = wl**2
    for A,B,C,D,E,F,G in coef:
        n.append(np.sqrt(A+B*wl2/(wl2 - C) + D*wl2/(wl2 - E) + F*wl2/(wl2 - G)))        
    return n

class Material:
    __init__(self):
        pass

class NBAF10(Material):
    def n(self, wl):
        


    
if __name__ == "__main__":
    print("test one: ")
    sellmeier()
    
    print("test two: ")
    try:
        sellmeier(1)
    except Exception as inst:
        print(type(inst))
        print(inst.args)
    
    print("test three: ")
    try:
        sellmeier('oops',12)
    except ValueError:
        print("handled")
    
    print("test four: ")
    sellmeier('LiNbO',20)
    
    print("test five: ")
    wlin = np.array([1,1.1,2])
    print(sellmeier('LiNbO',wlin))
    
