# Dynamic_mcnf_paper_code

This directory the code and the datasets used in the paper The dynamic unsplittable flow problem.
It contains all the presented algorithm, functions to create the instances and already created datasets.
The code in this directory is Python3 code. A Gurobi license is mandatory to use most of the solvers. The instances are stored using the Python module Pickle.

create_and_store_instances_dynamic.py
Contains functions to generate a custom dataset of instances

instance_mcnf.py
Contains functions to create graphs, commodity lists and thus create instances

launch_dataset_dynamic.py
Contains functions to launch algorithms on a dataset with the multiprocessing python library

mcnf_dynamic.py
Contains the solvers presented in the paper.

mcnf_dynamic_continuous.py
Contains functions the creates models for the linear relaxation of the dynamic unsplittable flow problem

mcnf_dynamic_column_generation.py
Contains functions the creates path-sequence formulations for the linear relaxation of the dynamic unsplittable flow problem and also functions solve these formulations with column generation

mcnf_do_test.py
Enables to create custom instances and launch algorithms on them

k_shortest_path.py
Contains an implementation of the k-shortest path algorithm of Jimenez et al

plot_result.py
Contains the code used to generate most of the figure presented in the paper
