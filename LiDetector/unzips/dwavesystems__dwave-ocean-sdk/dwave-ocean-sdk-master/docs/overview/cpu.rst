.. _using_cpu:

=================
Classical Solvers
=================

You might use a classical solver while developing your code or on a small version of
your problem to verify your code.
To solve a problem classically on your local machine, you configure a classical solver,
either one of those included in the Ocean tools or your own.

Examples
~~~~~~~~

Among several samplers provided in the :doc:`dimod </docs_dimod/sdk_index>`
tool for testing your code locally, is the :class:`~dimod.reference.samplers.ExactSolver` 
that calculates the energy of all
possible samples for a given problem. Such a sampler can solve a small three-variable
problem like the AND gate of the :ref:`formulating_bqm` section,

>>> import dimod
>>> bqm = dimod.BinaryQuadraticModel({'x1': 0.0, 'x2': 0.0, 'y1': 6.0},
...                  {('x2', 'x1'): 2.0, ('y1', 'x1'): -4.0, ('y1', 'x2'): -4.0},
...                  0, 'BINARY')

as follows:

>>> from dimod.reference.samplers import ExactSolver
>>> sampler = ExactSolver()
>>> response = sampler.sample(bqm)    
>>> print(response)       # doctest: +SKIP
  x1 x2 y1 energy num_oc.
0  0  0  0    0.0       1
1  1  0  0    0.0       1
3  0  1  0    0.0       1
5  1  1  1    0.0       1
2  1  1  0    2.0       1
4  0  1  1    2.0       1
6  1  0  1    2.0       1
7  0  0  1    6.0       1
['BINARY', 8 rows, 8 samples, 3 variables]

Note that the first four samples are the valid states of the AND gate and have
lower values than the second four, which represent invalid states.

If you use a classical solver running locally on your CPU, a single sample might provide
the optimal solution.

This example solves a two-variable problem using the :doc:`dwave_neal </docs_neal/sdk_index>`
simulated annealing sampler. For such a small problem, :code:`num_reads=10` most likely
finds the optimal solution.

>>> import neal
>>> solver = neal.SimulatedAnnealingSampler()
>>> sampleset = solver.sample_ising({'a': -0.5, 'b': 1.0}, {('a', 'b'): -1}, num_reads=10)
>>> sampleset.first.sample["a"] == sampleset.first.sample["b"] == -1
True
