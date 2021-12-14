.. _csp_sdk:

=======================
Constraint Satisfaction 
=======================

A `constraint satisfaction problem (CSP) <https://en.wikipedia.org/wiki/Constraint_satisfaction_problem>`_
requires that all the problem's variables be assigned
values, out of a finite domain, that result in the satisfying of all constraints.

The map-coloring CSP, for example, is to assign a color to each region of a map such that
any two regions sharing a border have different colors.

.. figure:: ../_images/Problem_MapColoring.png
   :name: Problem_MapColoring
   :alt: image
   :align: center
   :scale: 70 %

   Coloring a map of Canada with four colors.

The constraints for the map-coloring problem can be expressed as follows:

* Each region is assigned one color only, of :math:`C` possible colors.
* The color assigned to one region cannot be assigned to adjacent regions.

A finite domain CSP consists of a set of variables, a specification
of the domain of each variable, and a specification of the
constraints over combinations of the allowed values of the
variables. A constraint :math:`C_\alpha(\bf{x}_\alpha)` defined
over a subset of variables :math:`\bf{x}_\alpha` defines the set
of feasible and infeasible combinations of :math:`\bf{x}_\alpha`.
The constraint :math:`C_\alpha` may be be viewed as a predicate
which evaluates to true on feasible configurations and to false on
infeasible configurations. For example, if the domains of variables
:math:`X_1,X_2,X_3` are all :math:`\{0,1,2\}`, and the
constraint is :math:`X_1+X_2<X_3` then the feasible set is
:math:`\{(0,0,1),(0,0,2),(0,1,2),(1,0,2)\}`, and all remaining
combinations are infeasible.

Binary CSPs
-----------

Solving such problems as the map-coloring CSP on a :term:`sampler` such as the
D-Wave system necessitates that the
mathematical formulation use binary variables because the solution is implemented physically
with qubits, and so must translate to spins :math:`s_i\in\{-1,+1\}` or equivalent binary
values :math:`x_i\in \{0,1\}`. This means that in formulating the problem
by stating it mathematically, you might use unary encoding to represent the :math:`C` colors:
each region is represented by :math:`C` variables, one for each possible color, which
is set to value :math:`1` if selected, while the remaining :math:`C-1` variables are
:math:`0`.

Another example is logical circuits. Logic gates such as AND, OR, NOT, XOR etc
can be viewed as binary CSPs: the mathematically expressed relationships between binary inputs
and outputs must meet certain validity conditions. For inputs :math:`x_1,x_2` and
output :math:`y` of an AND gate, for example, the constraint to satisfy, :math:`y=x_1x_2`,
can be expressed as a set of valid configurations: (0, 0, 0), (0, 1, 0), (1, 0, 0),
(1, 1, 1), where the variable order is :math:`(x_1, x_2, y)`.

.. table:: Boolean AND Operation
   :name: BooleanANDAsPenalty

   ===============  ============================
   :math:`x_1,x_2`  :math:`y`
   ===============  ============================
   :math:`0,0`      :math:`0`
   :math:`0,1`      :math:`0`
   :math:`1,0`      :math:`0`
   :math:`1,1`      :math:`1`
   ===============  ============================

You can use Ocean's :doc:`dwavebinarycsp </docs_binarycsp/sdk_index>` to construct a :term:`BQM` from 
a CSP. It maps each individual constraint in the CSP to a ‘small’ Ising model or QUBO, in a mapping 
called a :doc:`penalty model </docs_penalty/sdk_index>`.

For more information on using the D-Wave system to solve CSPs, see the following documentation:

* :std:doc:`Getting Started with the D-Wave System <sysdocs_gettingstarted:doc_getting_started>`

   Introduces the use of QUBOs to represent constraints in some simple examples.
* :std:doc:`D-Wave Problem-Solving Handbook <sysdocs_gettingstarted:doc_handbook>`

   Provides a variety of techniques for, and examples of, reformulating CSPs as BQMs.





