# encoding=utf8
import random as rnd
import copy
import numpy as npx

__all__ = ['CuckooSearchAlgorithm']


class Cuckoo(object):
    """Defines cuckoo for population."""

    def __init__(self, D, LB, UB):
        self.D = D  # dimension of the problem
        self.LB = LB  # lower bound
        self.UB = UB  # upper bound
        self.Solution = []

        self.Fitness = float('inf')
        self.generateCuckoo()

    def generateCuckoo(self):
        self.Solution = [self.LB + (self.UB - self.LB) * rnd.random()
                         for _i in range(self.D)]

    def evaluate(self):
        self.Fitness = Cuckoo.FuncEval(self.D, self.Solution)

    def simpleBound(self):
        for i in range(self.D):
            if self.Solution[i] < self.LB:
                self.Solution[i] = self.LB
            if self.Solution[i] > self.UB:
                self.Solution[i] = self.UB

    def toString(self):
        pass

    def __eq__(self, other):
        return self.Solution == other.Solution and self.Fitness == other.Fitness


class CuckooSearchAlgorithm(object):
    r"""Cuckoo Search algorithm.

    Date: 12. 2. 2018

    Authors : Uros Mlakar

    License: MIT

    Reference paper: Yang, Xin-She, and Suash Deb. "Cuckoo search via Lévy flights."
    Nature & Biologically Inspired Computing, 2009. NaBIC 2009.

    TODO: Tests and validation!
    """

    def __init__(self, Np, D, nFES, Pa, Alpha, Lower, Upper, function):
        self.Np = Np
        self.D = D
        self.Pa = Pa
        self.Lower = Lower
        self.Upper = Upper
        self.Nests = []
        self.nFES = nFES
        self.FEs = 0
        self.Done = False
        self.Alpha = Alpha
        self.Beta = 1.5
        Cuckoo.FuncEval = staticmethod(function)

        self.gBest = Cuckoo(self.D, self.Lower, self.Upper)

    def evalNests(self):
        for c in self.Nests:
            c.evaluate()
            if c.Fitness < self.gBest.Fitness:
                self.gBest = copy.deepcopy(c)

    def initNests(self):
        for _i in range(self.Np):
            self.Nests.append(Cuckoo(self.D, self.Lower, self.Upper))

    def levyFlight(self, c):
        sigma = 0.6966
        u = npx.random.randn(1, self.D) * sigma
        v = npx.random.randn(1, self.D)
        step = u / (abs(v)**(1 / self.Beta))
        stepsize = self.Alpha * step * (npx.array(c.Solution) - npx.array(self.gBest.Solution)).flatten().tolist()

        c.Solution = (npx.array(c.Solution) + npx.array(stepsize) * npx.random.randn(1, self.D)).flatten().tolist()

    def tryEval(self, c):
        if self.FEs <= self.nFES:
            c.evaluate()
            self.FEs += 1
        else:
            self.Done = True

    def moveNests(self, Nests):
        MovedNests = []
        for c in Nests:
            self.levyFlight(c)
            c.simpleBound()
            self.tryEval(c)

            if c.Fitness < self.gBest.Fitness:
                self.gBest = copy.deepcopy(c)

            MovedNests.append(c)
        return MovedNests

    def resetNests(self, MovedNests):
        for _i in range(self.Np):
            if rnd.random() < self.Pa:
                m = rnd.randint(0, self.Np - 1)
                n = rnd.randint(0, self.Np - 1)

                newSolution = npx.array(MovedNests[_i].Solution) + (
                    rnd.random() * (npx.array(MovedNests[m].Solution) - npx.array(MovedNests[n].Solution))).flatten().tolist()
                MovedNests[_i].Solution = newSolution
                MovedNests[_i].simpleBound()
                self.tryEval(MovedNests[_i])
        return MovedNests

    def run(self):
        self.initNests()
        self.evalNests()
        self.FEs += self.Np
        while not self.Done:
            MovedNests = self.moveNests(self.Nests)
            self.Nests = self.resetNests(MovedNests)

        return self.gBest.Fitness