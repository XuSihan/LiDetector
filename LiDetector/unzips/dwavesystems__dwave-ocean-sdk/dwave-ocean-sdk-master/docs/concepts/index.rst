.. _concepts_sdk:

========
Concepts
========


See the :ref:`glossary` for short definitions of terminology or learn Ocean concepts here:

.. list-table:: Ocean Concepts
   :widths: auto
   :header-rows: 1

   * - Concepts
     - Related terms
   * - :ref:`bqm_sdk`
     - BQM, Ising, QUBO
   * - :ref:`csp_sdk`
     - CSP, binary CSP
   * - :ref:`dqm_sdk`
     - DQM, discrete quadratic model
   * - :ref:`hybrid_sdk`
     - quantum-classical hybrid, Leap's hybrid solvers, hybrid workflows
   * - :ref:`embedding_sdk`
     - embedding, mapping logical variables to physical qubits, chains, chain strength
   * - :ref:`topology_sdk`
     - Chimera, Pegasus
   * - :ref:`samplers_sdk`
     - solver
   * - :ref:`solutions_sdk`
     - samples, sampleset, probabilistic, energy

.. toctree::
   :hidden:
   :maxdepth: 1

   bqm
   csp
   dqm
   hybrid
   embedding
   topology
   samplers
   solutions
   

Glossary
--------

.. glossary::

      binary quadratic model
      BQM
         A collection of binary-valued variables  (variables that can be assigned two values, for example -1, 1) 
         with associated linear and quadratic biases. Sometimes referred to in other tools as a problem.
         See a fuller description under :doc:`Binary Quadratic Models </concepts/bqm>`.

      Chain
         One or more nodes or qubits in a target graph that represent a single variable in
         the source graph. See :term:`embedding`.
         See a fuller description under :doc:`Minor-Embedding </concepts/embedding>`.

      Chain length
         The number of qubits in a :term:`Chain`.
         See a fuller description under :doc:`Minor-Embedding </concepts/embedding>`.

      Chain strength
         Magnitude of the negative quadratic bias applied between variables to form a chain.
         See a fuller description under :doc:`Minor-Embedding </concepts/embedding>`.

      Chimera
         The D-Wave :term:`QPU` is a lattice of interconnected qubits. While some qubits
         connect to others via couplers, the D-Wave QPU is not fully connected.
         Instead, the qubits interconnect in an architecture known as Chimera.
         See a fuller description under :doc:`QPU Topology </concepts/topology>`.

      Complete graph
      Fully connected
          See `complete graph`_. on wikipedia. A fully connected or complete
          :term:`binary quadratic model` is one that has interactions between
          all of its variables.

          .. _complete graph: https://en.wikipedia.org/wiki/Complete_graph

      Composed sampler
          Samplers that apply pre- and/or post-processing to binary quadratic programs without
          changing the underlying :term:`sampler` implementation by layering composite patterns
          on the sampler. For example, a composed sampler might add spin transformations when
          sampling from the D-Wave system.

      Composite
          A :term:`sampler` can be composed. The
          `composite pattern <https://en.wikipedia.org/wiki/Composite_pattern>`_
          allows layers of pre- and post-processing to be applied to binary quadratic
          programs without needing to change the underlying sampler implementation.
          We refer to these layers as "composites". A composed sampler includes at least one
          sampler and possibly many composites.

      CSP
          Constraint satisfaction problem. A 
          `constraint satisfaction problem (CSP) <https://en.wikipedia.org/wiki/Constraint_satisfaction_problem>`_
          requires that all the problem's variables be assigned values, out of a finite domain, 
          that result in the satisfying of all constraints.
          See a fuller description under :doc:`QPU Topology </concepts/csp>`.

      discrete quadratic model
      DQM
         A collection of discrete-valued variables  (variables that can be 
         assigned the values specified by a set such as :math:`\{red, green, blue\}`
         or :math:`\{33, 5.7, 3,14 \}` ) with associated linear and quadratic biases. 
         See a fuller description under :doc:`Discrete Quadratic Models </concepts/dqm>`.

      Embed
      Embedding
      Minor-embed
      Minor-embedding
         The nodes and edges on the graph that represents an objective function
         translate to the qubits and couplers in :term:`Chimera`. Each logical qubit, in
         the graph of the :term:`objective function`, may be represented by one or more
         physical qubits. The process of mapping the logical qubits to physical
         qubits is known as minor embedding.
         See a fuller description under :doc:`Minor-Embedding </concepts/embedding>`.

      Excited state
         States of a quantum system that have higher energy than the :term:`ground state`.
         Such states represent non-optimal solutions for problems represented by an 
         :term:`Objective function` and infeasible configurations for problems 
         represented by a :term:`penalty model`.   

      Graph
         A collection of nodes and edges. A graph can be derived
         from a :term:`model`\ : a node for each variable and an edge for each pair
         of variables with a non-zero quadratic bias.

      Ground state
         The lowest-energy state of a quantum-mechanical system and the global minimum 
         of a problem represented by an :term:`Objective function`.  

      Hamiltonian
         A classical Hamiltonian is a mathematical description of some physical
         system in terms of its energies. We can input any particular state of
         the system, and the Hamiltonian returns the energy for that state.
         For a quantum system, a Hamiltonian is a function that maps certain states,
         called *eigenstates*, to energies. Only when the system is in an
         eigenstate of the Hamiltonian is its energy well defined and called
         the *eigenenergy*. When the system is in any other state, its energy
         is uncertain.
         For the D-Wave system, the Hamiltonian may be represented as

         .. math::
         	:nowrap:

         	\begin{equation}
         			{\cal H}_{ising} = \underbrace{\frac{A({s})}{2} \left(\sum_i {\hat\sigma_{x}^{(i)}}\right)}_\text{Initial Hamiltonian} + \underbrace{\frac{B({s})}{2} \left(\sum_{i} h_i {\hat\sigma_{z}^{(i)}} + \sum_{i>j} J_{i,j} {\hat\sigma_{z}^{(i)}} {\hat\sigma_{z}^{(j)}}\right)}_\text{Final Hamiltonian}
         	\end{equation}

         where :math:`{\hat\sigma_{x,z}^{(i)}}` are Pauli matrices operating on
         a qubit :math:`q_i`, and :math:`h_i` and :math:`J_{i,j}` are the qubit
         biases and coupling strengths.

      Hardware graph
         See `hardware graph`_. The hardware graph is the physical lattice of
         interconnected qubits. See also :term:`working graph`.
         See a fuller description under :doc:`QPU Topology </concepts/topology>`.

         .. _hardware graph: https://docs.dwavesys.com/docs/latest/c_gs_4.html

      Hybrid
         Quantum-classical hybrid is the use of both classical and quantum resources
         to solve problems, exploiting the complementary strengths that each provides.
         See :ref:`using_hybrid`.

      Ising
         Traditionally used in statistical mechanics. Variables are "spin up"
         (:math:`\uparrow`) and "spin down" (:math:`\downarrow`), states that
         correspond to :math:`+1` and :math:`-1` values. Relationships between
         the spins, represented by couplings, are correlations or anti-correlations.
         The :term:`objective function` expressed as an Ising model is as follows:

         .. math::
	          :nowrap:

	          \begin{equation}
	               \text{E}_{ising}(\pmb{s}) = \sum_{i=1}^N h_i s_i + \sum_{i=1}^N \sum_{j=i+1}^N J_{i,j} s_i s_j
	          \end{equation}

         where the linear coefficients corresponding to qubit biases
         are :math:`h_i`, and the quadratic coefficients corresponding to coupling
         strengths are :math:`J_{i,j}`.
         See also `Ising Model on Wikipedia <https://en.wikipedia.org/wiki/Ising_model>`_.

      Minimum gap
         The minimum distance between the :term:`ground state` and the first 
         :term:`excited state` throughout any point in the anneal.

      Model
         A collection of variables with associated linear and
         quadratic biases. Sometimes referred to as a **problem**.

      Objective function
         A mathematical expression of the energy of a system as a function of
         binary variables representing the qubits.

      Pegasus
         The D-Wave :term:`QPU` is a lattice of interconnected qubits. While some qubits
         connect to others via couplers, the D-Wave QPU is not fully connected.
         Instead, the qubits interconnect in an architecture known as Pegasus.
         See a fuller description under :doc:`QPU Topology </concepts/topology>`.

      Penalty function
         An algorithm for solving constrained optimization problems. In the context
         of Ocean tools, penalty functions are typically employed to increase the energy
         level of a problem’s :term:`objective function` by penalizing non-valid configurations.
         See `Penalty method on Wikipedia <https://en.wikipedia.org/wiki/Penalty_method>`_

      Penalty model
         An approach to solving constraint satisfaction problems (CSP) using an :term:`Ising` model 
         or a :term:`QUBO` by mapping each individual constraint in the CSP to a ‘small’ Ising model 
         or QUBO.

      QPU
         Quantum processing unit.

      QUBO
         Quadratic unconstrained binary optimization.
         QUBO problems are traditionally used in computer science. Variables
         are TRUE and FALSE, states that correspond to 1 and 0 values.
         A QUBO problem is defined using an upper-diagonal matrix :math:`Q`,
         which is an :math:`N` x :math:`N` upper-triangular matrix of real weights,
         and :math:`x`, a vector of binary variables, as minimizing the function

         .. math::
            :nowrap:

            \begin{equation}
              f(x) = \sum_{i} {Q_{i,i}}{x_i} + \sum_{i<j} {Q_{i,j}}{x_i}{x_j}
            \end{equation}

         where the diagonal terms :math:`Q_{i,i}` are the linear coefficients and
         the nonzero off-diagonal terms are the quadratic coefficients
         :math:`Q_{i,j}`.
         This can be expressed more concisely as

         .. math::
            :nowrap:

            \begin{equation}
              \min_{{x} \in {\{0,1\}^n}} {x}^{T} {Q}{x}.
            \end{equation}

         In scalar notation, the :term:`objective function` expressed as a QUBO
         is as follows:

         .. math::
            :nowrap:

            \begin{equation}
          		\text{E}_{qubo}(a_i, b_{i,j}; q_i) = \sum_{i} a_i q_i + \sum_{i<j} b_{i,j} q_i q_j.
            \end{equation}
         See also `QUBO on Wikipedia <https://en.wikipedia.org/wiki/Quadratic_unconstrained_binary_optimization>`_.

      Sampler
         Samplers are processes that sample from low energy states of a problem's objective
         function, which is a mathematical expression of the energy of a system. A binary
         quadratic model (BQM) sampler samples from low energy states in models such as those
         defined by an :term:`Ising` equation or a :term:`QUBO` problem and returns an iterable
         of samples, in order of increasing energy.

      SAPI
         Solver API used by clients to communicate with a :term:`solver`.

      Solver
         A resource that runs a problem. Some solvers interface to the :term:`QPU`;
         others leverage CPU and GPU resources.

      Source
      Source graph
         In the context of :term:`embedding`, the model or induced :term:`graph` that we
         wish to embed. Sometimes referred to as the **logical** graph/model.
         See a fuller description under :doc:`Minor-Embedding </concepts/embedding>`.

      Structured sampler
         Samplers that are restricted to sampling only binary quadratic models defined
         on a specific :term:`graph`.

      Subgraph
         See subgraph_ on wikipedia.

         .. _subgraph: https://en.wikipedia.org/wiki/Glossary_of_graph_theory_terms#subgraph

      Target
      Target graph
         :term:`Embedding` attempts to create a target :term:`model` from a target
         :term:`graph`. The process of embedding takes a source model, derives the source
         graph, maps the source graph to the target graph, then derives the target
         model. Sometimes referred to as the **embedded** graph/model.
         See a fuller description under :doc:`Minor-Embedding </concepts/embedding>`.

      Working graph
         In a D-Wave QPU, the set of qubits and couplers that are available for computation is known as the working graph. The yield of a working graph is typically less than 100% of qubits and couplers that are fabricated and physically present in the QPU. See :term:`hardware graph`.



