# This code sample is a result of my master's dissertation, called
# "Detection of rigid subchains in kinematic chains by means of matroid theory".
#
# This algorithm was implemented in the SageMath environment.
# https://www.sagemath.org/
#
# It is applied to check whether or not graphs representing
# mechanisms/machines contain rigid subchains.
# Because graphs with rigid subchains do not generate feasible results.

import time
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
from sage.graphs.graph_input import from_graph6
from sage.all import *

def mobility(rank, joints, screw_system):
    # The function computes the mobility of a chain.
    chain_mobility = screw_system*(rank - joints) + joints
    return chain_mobility

def no_rigid_subchains(my_graph, screw_system):
    # This function checks whether the chain contains rigid subchains

    # 1: Construct the matroid associated to the chain
    my_matroid = Matroid(my_graph.incidence_matrix(), ring=GF(2))
    my_groundset = my_matroid.groundset()
    my_rank = my_matroid.rank()

    # 2: Construct the dual matroid of the orginal matroid
    my_dual_matroid = my_matroid.dual()
    my_dual_rank = my_dual_matroid.rank()

    # 3: List all flats of the dual matroid
    for co_rank in range(0, my_dual_rank + 1):
        co_flats = my_dual_matroid.flats(co_rank)

        for co_flat in co_flats:
            # Let the sub_matroid be the matroid obtained from the orginal
            # matroid by deleting the elements of the co_flats
            sub_matroid = my_matroid.delete(co_flat)

            # 6: If the subchain is closed, compute
            # the mobility of the subchain
            if sub_matroid.is_connected():
                sub_groundset = sub_matroid.groundset()
                sub_rank = sub_matroid.rank()
                sub_joints = len(sub_groundset)
                sub_mobility = mobility(sub_rank, sub_joints, screw_system)

                # 7: Check if any proper subchain is rigid
                if sub_mobility <= 0 and sub_joints < len(my_groundset):
                    return False

    # 8: Otherwise, there are no rigid subchains
    return True

def number_assur(my_graph):
    # This function computes the number of orbits of the graph
    # each orbit candidate represents an Assur group
    graph_orbits = my_graph.automorphism_group(return_group=False, orbits=True)
    orbit_candidates = [vertex[0] for vertex in graph_orbits]
    number_orbits = len(orbit_candidates)
    number_orbits = str(number_orbits)

    return number_orbits

def graphs_from_txt(graph_path, graph_write):
    # This function imports rigid graphs from a text file,
    # checks whether the graph contains rigid subgraphs,
    # then returns the valid graphs to another text file,
    # classified by partitions.
    # The number of assur groups is also stored.
    with open(graph_path) as infile:
        for line in infile:

            # Build a graph from a graph6 string
            g6_string = line.replace(line[-1], "")
            my_graph = Graph()
            from_graph6(my_graph, g6_string)

            # Compute the graph partition
            graph_deg_sequence = my_graph.degree_sequence()
            partition = [graph_deg_sequence.count(i) for i
                        in range(2, max(graph_deg_sequence) + 1)]

            # Check wheter the graph contains rigid subchains,
            # Then store the string in the correct graph partition
            # Store also the number of associated assur groups
            if no_rigid_subchains(my_graph, screw_system = 3):
                with open(graph_write + 'baranov_' + str(partition), "a") \
                          as baranov_file:
                    baranov_file.write(g6_string + '\n')

                assur_per_graph = number_assur(my_graph)
                with open(graph_write + 'assur_' + str(partition), "a") \
                          as assur_file:
                    assur_file.write(assur_per_graph + '\n')

def list_subfiles(my_path):
    # This function lists all the text files that will
    # be used as input for the graph filtering process.
    input_files = [graph_file for graph_file in listdir(my_path)
                   if isfile(join(my_path, graph_file))]

    try:
        input_files.remove('desktop.ini')
    except Exception:
        pass

    input_files = [my_path + graph_file for graph_file in input_files]
    return input_files

def process(graph_path):
    # This function calls the graph filtering process,
    # which will proceed in parallel.
    graph_write = 'my_output/'
    graphs_from_txt(graph_path, graph_write)

# MAP THE INPUT FILE LIST
input_path = 'my_input/'
input_files = list_subfiles(input_path)

# GET THEM TO WORK IN PARALLEL
# Assuming you want to use 8 processors
num_processors = 8

# Create a pool of processors
p=Pool(processes = num_processors)

start = time.time()
output = p.map(process, input_files)
end = time.time()

print(end - start)
