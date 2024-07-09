#!/usr/bin/env python

# ptx_matrix_decomp - decompose a ptx matrix using things like ICA
#
# Author: Saad Jbabdi <saad@fmrib.ox.ac.uk>
#         Rogier Mars <rogier.mars@ndcn.ox.ac.uk>
#
# Copyright (C) 2023 University of Oxford
# SHBASECOPYRIGHT

import argparse
import os
import numpy as np
from ptx_matrix_tools import utils


def parse_cmdline_args():
    p = argparse.ArgumentParser("ptx_matrix_decomp")
    p.add_argument('--ptxdir', required=True, nargs='+', metavar='<STR>', type=str, help="ProbTrackx Folder(s), or ascii list of folders")
    p.add_argument('--outdir', required=True, metavar='<STR>', type=str, help="Output Folder")
    p.add_argument('--dim', required=True, metavar='<INT>', type=int, help="Number of dimensions")

    # Some optional arguments to be added here
    p.add_argument('--ptx_seeds', required=False, nargs='+', metavar='<NIFTI or GIFTI>', type=str, help="Seeds used in PTX (if not provided, these will be taken from the log file)")
    p.add_argument('--migp', required=False, default=1000, metavar='<INT>', type=int, help="MIGP dimensionality (default is 1000. set to negative to skip MIGP)")
    p.add_argument('--mode', required=False, default='dualreg', type=str, help="What to do when provided with a list of ptx_folders. Options are 'dualreg' (default - runs decomp on average and produces single subject decomp using dual regression) or 'average' (only produces decomp of the average)")
    p.add_argument('--algo', required=False, default='ICA', type=str, help="What algorithm to run. Options are: ICA (default), or NMF.")
    p.add_argument('--wta', action='store_true', help="Save winner-takes-all maps")
    p.add_argument('--wta_zthr', required=False, default=0., type=float, help="Winner-takes-all threshold (default=0.)")
    p.add_argument("-N", "--normalise", dest='normalise', action='store_true', required=False, default=False, help="normalise components by scaling")
    p.add_argument("-S", "--sign_flip", dest='sign_flip', action='store_true', required=False, default=False, help="sign flip components")

    # If a design is provided, run the stats
    p.add_argument('--glm_mat', required=False, metavar='<design.mat>', help="Run a GLM using design and contrast matrices provided (only in dualreg mode)")
    p.add_argument('--glm_con', required=False, metavar='<design.con>', help="Run a GLM using design and contrast matrices provided (only in dualreg mode)")


    return p.parse_args()


def main():
    args = parse_cmdline_args()

    # Import after parsing argument to speed up printing help message

    out_folder = args.outdir
    # Create out_folder if it does not exist already
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder, exist_ok=True)
    # check that I'll be able to save results
    if not os.access(out_folder, os.W_OK):
        raise(Exception(f'Cannot write into {out_folder}. Check permissions...'))


    # Save command line options
    #with open(os.path.join(out_folder, "options.txt"), "w") as f:
    #    f.write(parser.format_values())

    # begin
    print("---- PTX Matrix2 Decomposition ----")
    ptx_folder = args.ptxdir

    group_mode = False
    # if len = 1 --> could be text file or single folder
    if len(ptx_folder) == 1:
        if not os.path.isdir(ptx_folder[0]):
            with open(ptx_folder[0], 'r') as f:
                ptx_folder = [x.strip() for x in f.read().split(' ')]
    if len(ptx_folder) == 1:
        print('...Single ptx_folder provided')
    else:
        group_mode = True
        print('...List of ptx_folders provided')
    print(ptx_folder)

    # check that I can find the seed files
    seeds = args.ptx_seeds
    if seeds is None:
        if group_mode:
            raise(Exception('Must provide seeds if running in group mode.'))
        seeds = utils.get_seed(ptx_folder[0])
    print(f'...Seed files are: {seeds}')
    for s in seeds:
        if not utils.is_nifti(s) and not utils.is_gifti(s):
            raise(Exception(f'Seed file {s} does not appear to be a valid GIFTI or NIFTI'))

    # Load the matrix
    if group_mode:
        # Calculate the group average matrix
        list_of_matrices = [os.path.join(f, 'fdt_matrix2.dot') for f in ptx_folder]
        print('... Averaging subject matrices')
        t = utils.timer()
        t.tic()
        C = utils.avg_matrix2(list_of_matrices)
    else:
        # Load a single matrix
        C = utils.load_mat2(os.path.join(ptx_folder[0], 'fdt_matrix2.dot'))
        
    print(f'...loaded matricies in {t.toc()} secs.')

    # Run the decomposition
    n_comps = args.dim
    kwargs = {
        'do_migp': args.migp > 0,
        'd_pca': args.migp,
        'n_dim': args.migp,
        'algo': args.algo,
        'normalise': args.normalise,
        'sign_flip': args.sign_flip
    }

    # Run the decomposition
    G, W = utils.matrix_decomposition(C, n_components=n_comps, **kwargs)

# Save the results
    # If group mode, save average then run dualreg to save the individual stuff (if user requested)
    if group_mode:
        print("...Saving group average results")
    else:
        print("...Saving group decomposition results")
    utils.save_W( W, ptx_folder[0], os.path.join(out_folder, f'W_dim{n_comps}') )
    utils.save_G( G, ptx_folder[0], os.path.join(out_folder, f'G_dim{n_comps}'), seeds=seeds)

    if args.wta:
        # Save winner-takes-all maps
        print("...Saving winner-take-all maps")
        W_wta = utils.winner_takes_all(W, axis=0, z_thr = args.wta_zthr)
        G_wta = utils.winner_takes_all(G, axis=1, z_thr = args.wta_zthr)
        utils.save_W( W_wta, ptx_folder[0], os.path.join(out_folder, f'W_dim{n_comps}_wta') )
        utils.save_G( G_wta, ptx_folder[0], os.path.join(out_folder, f'G_dim{n_comps}_wta'), seeds=seeds)

    glm_data = {'dualreg_on_G':[], 'dualreg_on_W' : []} # stores data for glm if user wants to run that
    if group_mode:
        # Only run the dual regression if the user asked for it
        if args.mode == 'dualreg':
            print('...Doing dual regression')
            os.makedirs(os.path.join(out_folder,'dualreg_on_G'), exist_ok=True)
            os.makedirs(os.path.join(out_folder,'dualreg_on_W'), exist_ok=True)
            for idx, matfile in enumerate(list_of_matrices):
                print(f'... subj-{idx} - mat: {matfile}')
                idx3 = str(idx).zfill(3) # zero-pad index
                Cs = utils.load_mat2(os.path.join(matfile))

                # dual reg on G
                Gs, Ws = utils.dualreg(Cs, G)
                out_dualreg = os.path.join(out_folder,'dualreg_on_G')
                utils.save_W( Ws, ptx_folder[idx], os.path.join(out_dualreg, f'Ws_{idx3}_dim{n_comps}') )
                utils.save_G( Gs, ptx_folder[idx], os.path.join(out_dualreg, f'Gs_{idx3}_dim{n_comps}'), seeds=seeds)
                # keep data for GLM?
                if args.glm_mat:
                    glm_data['dualreg_on_G'].append([Gs, Ws])

                # dual reg on W
                Gs, Ws = utils.dualreg(Cs, W)
                out_dualreg = os.path.join(out_folder,'dualreg_on_W')
                utils.save_W( Ws, ptx_folder[idx], os.path.join(out_dualreg, f'Ws_{idx3}_dim{n_comps}') )
                utils.save_G( Gs, ptx_folder[idx], os.path.join(out_dualreg, f'Gs_{idx3}_dim{n_comps}'), seeds=seeds)
                if args.glm_mat:
                    glm_data['dualreg_on_W'].append([Gs, Ws])

                # memory management
                del Cs


    # GLM?
    if args.glm_mat:
        print('...Running GLMs')
        if not group_mode:
            raise(Exception('Must provide multiple subjects data to run a GLM'))
        if args.mode != 'dualreg':
            raise(Exception('Must be in dualreg mode to run a GLM'))
        # Load design files
        from fsl.data.vest import loadVestFile
        desmat = loadVestFile(args.glm_mat)
        conmat = loadVestFile(args.glm_con)
        glm = utils.GLM()
        # Loop through dualreg targets
        for dr_target in ['G', 'W']:
            # Loop through dimensions and run GLMs
            out_glm = os.path.join(out_folder, f'glm_on_{dr_target}')
            os.makedirs(out_glm, exist_ok=True)
            all_stats = {'G' : [], 'W' : []}
            for comp in range(n_comps):
                # assemble data matrix subject-by-gm or subject-by-wm
                data = {
                    'G': np.array( [ glm_data[f'dualreg_on_{dr_target}'][i][0][:, comp] for i in range(len(list_of_matrices)) ] ),
                    'W': np.array( [ glm_data[f'dualreg_on_{dr_target}'][i][1][comp, :] for i in range(len(list_of_matrices)) ] )
                }
                for y in data:
                    glm.fit(desmat, data[y])
                    stats = glm.calc_stats(conmat)
                    all_stats[y].append(stats)

            # save results
            for stat in ['tstat', 'zstat', 'pval']:
                for y in ['G', 'W']:
                    X = np.asarray([s[stat] for s in all_stats[y]])  # n_comps x n_contrasts x n_voxels
                    X = np.transpose(X, (1, 2, 0))
                    for con in range(X.shape[0]):
                        if y == 'G':
                            utils.save_G(X[con], ptx_folder[0], os.path.join(out_glm, f'{y}_{stat}{con+1}'), seeds=seeds)
                        elif y == 'W':
                            utils.save_W(X[con].T, ptx_folder[0], os.path.join(out_glm, f'{y}_{stat}{con+1}'))
    print("---- Done ----")

if __name__ == '__main__':
    main()
