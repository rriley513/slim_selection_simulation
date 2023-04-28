import msprime
import numpy as np
import pyslim
import sys
import tskit

import global_vars

# TODO: optparse for Ne, reco_path, use default value for mut

num_haps = 198
num_inds = num_haps//2 # dihaploid

def main(filelist, SUFFIX):
    # TODO: output N recombination rates to a file, read those in

    files = open(filelist, 'r').readlines()
    n_regions = len(files)
    n_range = range(n_regions)
    # TODO: reco values numpy array will be created specifically for the tree set
    reco_values = np.load(reco_values_path) 
    # (N, 36, 198)
    matrices = np.zeros((n_regions, global_vars.NUM_SNPS, num_haps))
    distances = np.zeros((n_regions, global_vars.NUM_SNPS))
    
    matrices_list = [None for i in n_range]
    distances_list = [None for i in n_range]

    max_SNPs = -1
        
    # for file_name in files:
    for i in n_range:
        # file_name = file_name[:-1]
        file_name = files[i][:-1] # eliminate newline char
        reco = reco_values[i]
        
        use_selection = "sel" in file_name

        ts = pyslim.update(tskit.load(file_name))
        ts = clean_tree(ts, use_selection)

        gt_matrix = ts.genotype_matrix()
        num_snps_present = gt_matrix.shape[0]
        dist_vec = get_dist_vec(ts, num_snps_present)

        print(file_name + " " + str(num_snps_present))
                
        # store for region_len first
        matrices_list[i] = gt_matrix
        distances_list[i] = dist_vec        

        if max_SNPs < num_snps_present:
            max_SNPs = num_snps_present
            
        # now trim/pad
        if num_snps_present < global_vars.NUM_SNPS:
            gt_matrix, dist_vec = center_pad(gt_matrix, dist_vec, num_snps_present, global_vars.NUM_SNPS)
        elif num_snps_present > global_vars.NUM_SNPS:
            gt_matrix, dist_vec = trim_matrix(gt_matrix, dist_vec, num_snps_present)
        
        matrices[i] = gt_matrix
        distances[i] = dist_vec

    # finish regions_len section ----------------------------
    assert len(matrices_list) == n_regions
    print("seting up matrices: max SNPs = " + str(max_SNPs) + ", num matrices = " + str(n_regions))
    
    matrices_regions = np.zeros((n_regions, max_SNPs, num_haps))
    distances_regions = np.zeros((n_regions, max_SNPs))

    for j in n_range:
        print(j)
        gt_matrix = matrices_list[j]
        dist_vec = distances_list[j]
        num_snps_present = gt_matrix.shape[0]

        assert num_snps_present <= max_SNPs

        if num_snps_present < max_SNPs:
            gt_matrix, dist_vec = center_pad(gt_matrix, dist_vec, num_snps_present, max_SNPs)

        matrices_regions[j] = gt_matrix
        distances_regions[j] = dist_vec

    np.save("matrices_"+SUFFIX, matrices)
    np.save("distances_"+SUFFIX, distances)
    
    np.save("matrices_regions_"+SUFFIX, matrices_regions)
    np.save("distances_regions_"+SUFFIX, distances_regions)    
    
'''
necessary step. Do not remove.
'''
def clean_tree(ts, selection):
    ts_recap = pyslim.recapitate(ts, recombination_rate=params["reco"],
                                 ancestral_Ne=params["Ne"])

    if selection:
        ts_simplified = simplify_selection_tree(ts_recap)
    else:
        ts_simplified = simplify_tree(ts_recap)
    ts_mutated = msprime.mutate(ts_simplified, rate=params["mut"], keep=True)
    return ts_mutated

'''
part of above necessary step
'''
def simplify_tree(ts_recap):   
    # alive_inds = ts_recap.individuals_alive_at(0)
    alive_inds = np.array([i for i in range(ts_recap.num_individuals)])
    keep_inds = np.random.choice(alive_inds, num_inds, replace=False)
    keep_nodes = []

    for i in keep_inds:
        keep_nodes.extend(ts_recap.individual(i).nodes)

    ts_simplified = ts_recap.simplify(keep_nodes)
    return ts_simplified

def simplify_selection_tree(ts_recap):
    tries = 0
    num_muts = 0
    
    while num_muts < 1:
        tries += 1
        ts_simplified = simplify_tree(ts_recap)
        num_muts = ts_simplified.genotype_matrix().shape[0]
        print(tries)

    return ts_simplified

def trim_matrix(gt_matrix, dist_vec, num_snps_present):
    assert type(dist_vec) == type(np.array([]))

    half_snps_present = num_snps_present//2
    half_S = global_vars.NUM_SNPS//2

    new_matrix = gt_matrix[half_snps_present - half_S : half_snps_present + half_S]
    # note: we DON'T adjust the distance vector
    new_dist = dist_vec[half_snps_present - half_S : half_snps_present + half_S]
    
    return new_matrix, new_dist

def get_dist_vec(ts, snps_total):
    positions = [round(variant.site.position) for variant in ts.variants()]
    assert len(positions) == snps_total
    
    dist_vec = [0] + [(positions[j+1] - positions[j])/ \
              global_vars.L for j in range(snps_total-1)]
    return np.array(dist_vec)
    
def center_pad(gt_matrix, dist_vec, num_snps_present, S):
    inds = gt_matrix.shape[1]
    half_snps_present = num_snps_present//2
    if num_snps_present % 2 == 0:
        other_half_snps_present = half_snps_present
    else:
        other_half_snps_present = half_snps_present + 1

    half_S = S//2
    if S % 2 == 0 or (num_snps_present % 2 == 1 and S % 2 == 1) or num_snps_present % 2 == 0:
        other_half_S = half_S
    else:
        other_half_S = half_S+1 # even/odd
            

    new_matrix = np.zeros((S, inds))
    new_dist = np.zeros((S))

    new_matrix[half_S - half_snps_present : other_half_S + other_half_snps_present] = gt_matrix
    new_dist[half_S - half_snps_present : other_half_S + other_half_snps_present] = dist_vec

    return new_matrix, new_dist

if __name__ == "__main__":
    # test_center_pad()
    # test_trim_matrix()

    filelist = sys.argv[1]

    SUFFIX = sys.argv[2]
    
    main(filelist, SUFFIX)
