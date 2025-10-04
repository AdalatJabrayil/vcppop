# Partial-Ordering Based ILP and SAT Models for the Vertex Coloring Problem

This repository provides implementations of ILP and SAT models to solve the classic Vertex Coloring Problem (VCP).

The models, based on a partial ordering approach from recent research in the field, are organized in the src/ directory.

    src/
    ├── vcp_pop2.py      # ILP model POP2 [1]
    ├── vcp_poph2.py     # ILP model POPH2 [1]
    ├── vcp_pop_sat.py   # SAT model POP-S [2]
    ├── vcp_poph_sat.py  # SAT model POPH-S [2]


## Requirements

- Python 3
- [NetworkX](https://networkx.org/) (Python library)
- [Gurobi Optimizer](https://www.gurobi.com/) and Python interface `gurobipy` (for ILP models)
- [Kissat SAT Solver](https://github.com/arminbiere/kissat) (for SAT models)



## Running the Models

To solve a VCP instance using one of the models, use the provided `runModel.sh` script:

    $ ./runModel.sh M I [Options...]

    where:

    M — name of the model file (e.g. vcp_pop2.py, vcp_poph_sat.py)
    I — input graph instance in DIMACS .col format
    [Options...] — optional flags or settings

    Options:

    - t=N          | Set a time limit of `N` seconds (e.g. `t=3600`)
    - BINARYSEARCH | Use binary search in SAT models (default is linear upward search)


## Examples

    # Run ILP model POP2 on instance ash331GPIA.col with default time limit (1 hour)
    $ ./runModel.sh vcp_pop2.py ash331GPIA.col

    # Run SAT model POP-S on the same instance with a 10-minute limit
    $ ./runModel.sh vcp_pop_sat.py ash331GPIA.col t=600

    # Run SAT model POP-S with a 10-minute limit and binary search enabled
    $ ./runModel.sh vcp_pop_sat.py ash331GPIA.col t=600 BINARYSEARCH


## References

- [1] A. Jabrayilov and P. Mutzel (2022).
  Strengthened Partial-Ordering Based ILP Models for the Vertex Coloring Problem.
  DOI: [10.48550/ARXIV.2206.13678](https://doi.org/10.48550/arXiv.2206.13678)

- [2] D. Faber, A. Jabrayilov, and P. Mutzel (2024).
  SAT Encoding of Partial Ordering Models for Graph Coloring Problems.
  In: 27th International Conference on Theory and Applications of Satisfiability Testing (SAT 2024).
  DOI: [10.4230/LIPIcs.SAT.2024.12](https://doi.org/10.4230/LIPIcs.SAT.2024.12)
