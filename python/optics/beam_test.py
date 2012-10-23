import unittest
from pylab import *
from optics.beam import *
import copy

class TestBeam(unittest.TestCase):

    def setUp(self):
        # setup the objects/parameters you want to test
        self.B1 = Beam(p=10e-3, wl=780e-9, w=1e-3, r=float('inf'))

    def test_init_method_2(self):
        B1 = self.B1
        d1 = 3e-3
        d2 = 5e-3
        r1 = B1.prop(Space(d1)).r
        r2 = B1.prop(Space(d2 - d1)).r

        B2 = Beam(p=B1.p, wl=B1.wl, d1=d1, d2=d2, r1=r1, r2=r2)
        are_beams_equla(B1, B2)
        self.assertAlmostEqual(B1.r, B2.r, 7) 

    def test_init_method_3(self):
        B1 = self.B1
        d1 = 3e-3
        d2 = 5e-3
        r1 = B1.prop(Space(d1)).r
        r2 = B1.prop(Space(d2 - d1)).r

        B2 = Beam(p=B1.p, wl=B1.wl, d1=d1, d2=d2, w1=w1, w2=w2)
        are_beams_equla(B1, B2)
        for var in Beam._beam_vars:
            self.assertAlmostEqual(B1.property(var), B2.property(var), 7) 

    def are_beams_equal(B1, B2):
        for var in Beam._beam_vars:
            self.assertAlmostEqual(B1.property(var), B2.property(var), 7) 
        

# running the module from the commandline will make the unittests interactive
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBeam)
    unittest.TextTestRunner(verbosity=5).run(suite)
