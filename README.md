# NFACT

*This is a repo merging NFacT (Shaun Warrington, Ellie Thompson, and Stamatios Sotiropoulos) and ptx_decomp (Saad Jbabdi and Rogier Mars).*

## What is NFACT

NFACT (Non-negative matrix Factorisation of Tractography data) is a set of modules (as well as an end to end pipeline) that decomposes 
tractography data using NMF/ICA.

It consists of three "main" decomposition modules:
    
    - nfact_pp (Pre-process data for decomposition)
    
    - nfact_decomp (Decomposes a single or average group matrix using NMF or ICA)
    
    - nfact_dr (Dual regression on group matrix)

as well as three axillary "modules":
    
    - nfact_config (creates config files for the pipeline and changing any hyperparameters)
    
    - nfact_Qc (Creates hitmaps to check for bias in decomposition)

    - nfact_glm (To run hypothesis testing)
and a pipeline wrapper
    
    - nfact (runs either all three pre-processing modules or just nfact_decomp and nfact_dr)

-----------------------------------------------------------------------------------------------------------------------------------------------------------

``` 
 _   _ ______   ___   _____  _____    
| \ | ||  ___| /   \ /  __ \|_   _|    
|  \| || |_   / /_\ \| /  \/  | |      
|     ||  _|  |  _  || |      | |    
| |\  || |    | | | || \__/\  | |    
\_| \_/\_|    \_| |_/ \____/  \_/ 
```

## NFACT pipeline

This pipeline runs nfact_pp, nfact_decomp and nfact_dr on tractography data that has been processed by bedpostx. 


The pipeline first creates the omatrix2 


### Usage:

```
usage: nfact [-h] [-l LIST_OF_SUBJECTS] [-s SEED [SEED ...]] [-c CONFIG] [-S] [-i REF] [-b BPX_PATH] [-w WARPS [WARPS ...]] [-r ROIS [ROIS ...]] [-t TARGET2] [-d DIM] [-o OUTDIR] [-a ALGO]

options:
  -h, --help            show this help message and exit

Inputs:
  -l LIST_OF_SUBJECTS, --list_of_subjects LIST_OF_SUBJECTS
                        Filepath to a list of subjects.
  -s SEED [SEED ...], --seed SEED [SEED ...]
                        A single or list of seeds
  -c CONFIG, --config CONFIG
                        An nfact_config file. If this is provided no other arguments are needed.
  -S, --skip            Skips NFACT_PP. Pipeline still assumes that NFACT_PP has been ran before.

PP:
  -i REF, --image_standard_space REF
                        Standard space reference image
  -b BPX_PATH, --bpx BPX_PATH
                        Path to Bedpostx folder inside a subjects directory.
  -w WARPS [WARPS ...], --warps WARPS [WARPS ...]
                        Path to warps inside a subjects directory (can accept multiple arguments)
  -r ROIS [ROIS ...], --rois ROIS [ROIS ...]
                        A single or list of ROIS
  -t TARGET2, --target TARGET2
                        Path to target image. If not given will create a whole mask from reference image

decomp:
  -d DIM, --dim DIM     Number of dimensions/components
  -o OUTDIR, --outdir OUTDIR
                        Path to where to create an output folder
  -a ALGO, --algo ALGO  What algorithm to run. Options are: ICA (default), or NMF.

```

example call:

```
nfact --list_of_subject /absolute path/sub_list \
--seed thalamus.nii.gz \
--algo NMF \
--dim 100 \
--outdir /absolute path/save directory \
--warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz \
--ref $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz \
--bpx Diffusion.bedpostX 
```

With a config file:
```
nfact –config /absolute path/nfact_config.config  
```
-----------------------------------------------------------------------------------------------------------------------------------------------------------

```
 _   _ ______   ___   _____  _____     ______ ______
| \ | ||  ___| /   \ /  __ \|_   _|    | ___ \| ___ \
|  \| || |_   / /_\ \| /  \/  | |      | |_/ /| |_/ /
|     ||  _|  |  _  || |      | |      |  __/ |  __/
| |\  || |    | | | || \__/\  | |      | |    | |
\_| \_/\_|    \_| |_/ \____/  \_/      \_|    \_|

```
## NFACT PP
Pre-processing of tractography data for decomposition with NFACT (Non-negative matrix Factorisation of Tractography data)

Under the hood NFACT PP is probtrackx2 omatrix2 option to get a seed by target connectivity matrix 

### Input for nfact_preproc

Required before running NFACT PP:
    - crossing-fibre diffusion modelled data (bedpostX)
    - Seeds (either surfaces or volumes)

NFACT PP has three modes: surface , volume, and filestree.

Required input:
    - List of subjects
    - Output directory

Input needed for filetree mode:
    - .tree file (NFACT_PP comes with some defaults such as hcp)

Input needed for both surface and volume mode:
    - Seeds path inside folder
    - Warps path inside a subjects folder
    - bedpostx folder path inside a subjects folder
   
Input for surface seed mode:
    - Seeds as surfaces
    - ROIs as surfaces (medial wall)
    
Input needed for volume mode:
    - Seeds as volumes 

 ### NFACT PP input folder 

NFACT pp can be used in a folder agnostic way by providing the paths to seeds/bedpostX/target inside a subject folder (i.e --seeds seeds/amygdala.nii.gz).

The other way is to use the --file_tree command with the name of a file tree (see https://open.win.ox.ac.uk/pages/fsl/file-tree/index.html for further details on filetree).
In this case seeds/rois/bedpostx do not need to be specified as nfact_pp will try and find the appropriate files.

```
nfact_pp --file_tree hcp --list_of_subjects /home/study/list_of_subjects
```

Filetrees are saved in filetrees folder in nfact, so custom filetrees can be put there and called similar to the command above. NFACT_PP currently has a built in a filetree for HCP and a hcp_qunex (HCP in qunex format) to perform full brain tractography. 

Use of custom filetree
-----------------------
seed files are aliased as (seed), roi as (roi), warps as (diff2std, std2diff) and bedpostX as (bedpostX). Two seeds are supported if the seeds are bilateral indicated with {hemi}.seed, with the actual seed names being L.seed.nii.gz/R.seed.nii.gz. A singe seed can be given as well.

### Usage:

```
options:
  -h, --help            show this help message and exit
  -hh, --verbose_help   Prints help message and example usages
  -O, --overwrite       Overwrite previous file structure

Compulsory Arguments:
  -l LIST_OF_SUBJECTS, --list_of_subjects LIST_OF_SUBJECTS
                        A list of subjects in text form. If not provided NFACT PP will use all subjects in the study folder. All subjects need full file path to subjects directory
  -o OUTDIR, --outdir OUTDIR
                        Directory to save results in

REQUIRED FOR FILETREE MODE: :
  -f FILE_TREE, --file_tree FILE_TREE
                        Use this option to provide name of predefined file tree to perform whole brain tractography. NFACT_PP currently comes with HCP filetree. See documentation for further information.

Tractography options: :
  -s SEED [SEED ...], --seed SEED [SEED ...]
                        A single or list of seeds
  -w WARPS [WARPS ...], --warps WARPS [WARPS ...]
                        Path to warps inside a subjects directory (can accept multiple arguments)
  -b BPX_PATH, --bpx BPX_PATH
                        Path to Bedpostx folder inside a subjects directory.
  -r ROI [ROI ...], --roi ROI [ROI ...]
                        REQUIRED FOR SURFACE MODE: ROI(s) (.gii files) to restrict seeding to (e.g. medial wall masks).
  -sr SEEDREF, --seedref SEEDREF
                        Reference volume to define seed space used by probtrackx. Default is MNI space.
  -t TARGET2, --target TARGET2
                        Name of target. If not given will create a whole mask from reference image
  -ns NSAMPLES, --nsamples NSAMPLES
                        Number of samples per seed used in tractography (default = 1000)
  -mm MM_RES, --mm_res MM_RES
                        Resolution of target image (Default = 2 mm)
  -p PTX_OPTIONS, --ptx_options PTX_OPTIONS
                        Path to ptx_options file for additional options
  -e EXCLUSION, --exclusion EXCLUSION
                        Path to an exclusion mask. Will reject pathways passing through locations given by this mask
  -S [STOP ...], --stop [STOP ...]
                        Use wtstop and stop in the tractography. Takes a file path to a json file containing stop and wtstop masks, JSON keys must be stopping_mask and wtstop_mask. Argument can be used with the --filetree, in that case no json file is needed.

Parallel Processing arguments:
  -n N_CORES, --n_cores N_CORES
                        If should parallel process locally and with how many cores. This parallelizes the number of subjects. If n_cores exceeds subjects nfact_pp sets this argument to be the number of subjects. If nfact_pp is being used on one subject then this may
                        slow down processing.

Cluster Arguments:
  -C, --cluster         Use cluster enviornment
  -cq CLUSTER_QUEUE, --queue CLUSTER_QUEUE
                        Cluster queue to submit to
  -cr CLUSTER_RAM, --cluster_ram CLUSTER_RAM
                        Ram that job will take. Default is 60
  -ct CLUSTER_TIME, --cluster_time CLUSTER_TIME
                        Time that job will take. nfact_pp will assign a time if none given
  -cqos CLUSTER_QOS, --cluster_qos CLUSTER_QOS
                        Set the qos for the cluster


Example Usage:
    Surface mode:
           nfact_pp --list_of_subjects /home/study/sub_list
               --outdir /home/study
               --bpx_path /path_to/.bedpostX
               --seeds /path_to/L.white.32k_fs_LR.surf.gii /path_to/R.white.32k_fs_LR.surf.gii
               --roi /path_to/L.atlasroi.32k_fs_LR.shape.gii /path_to/R.atlasroi.32k_fs_LR.shape.gii
               --warps /path_to/stand2diff.nii.gz /path_to/diff2stand.nii.gz
               --n_cores 3

    Volume mode:
            nfact_pp --list_of_subjects /home/study/sub_list
                --bpx_path /path_to/.bedpostX
                --seeds /path_to/L.white.nii.gz /path_to/R.white.nii.gz
                --warps /path_to/stand2diff.nii.gz /path_to/diff2stand.nii.gz
                --ref MNI152_T1_1mm_brain.nii.gz
                --target dlpfc.nii.gz

    Filestree mode:
        nfact_pp --filestree hcp
            --list_of_subjects /home/study/sub_list
            --outdir /home/study
            --n_cores 3

```

------------------------------------------------------------------------------------------------------------------------------------------

```
 _   _ ______   ___   _____  _____  ______  _____  _____  _____ ___  ___ _____
| \ | ||  ___| / _ \ /  __ \|_   _| |  _  \|  ___|/  __ \|  _  ||  \/  || ___ \
|  \| || |_   / /_\ \| /  \/  | |   | | | || |__  | /  \/| | | || .  . || |_/ /
| . ` ||  _|  |  _  || |      | |   | | | ||  __| | |    | | | || |\/| ||  __/
| |\  || |    | | | || \__/\  | |   | |/ / | |___ | \__/\\ \_/ /| |  | || |
\_| \_/\_|    \_| |_/ \____/  \_/   |___/  \____/  \____/ \___/ \_|  |_/\_|

```
## NFACT decomp
This is the main decompoisition module of NFACT. Runs either ICA or NMF and saves the components. Components can also be normalised and winner takes all maps
created.


### Usage
```
options:
  -h, --help            show this help message and exit
  -l LIST_OF_SUBJECTS, --list_of_subjects LIST_OF_SUBJECTS
                        REQUIRED: Filepath to a list of subjects. List can contain a single subject.
  -o OUTDIR, --outdir OUTDIR
                        REQUIRED: Path to output folder
  -d DIM, --dim DIM     REQUIRED: Number of dimensions/components
  --seeds SEEDS, -s SEEDS
                        REQUIRED: File of seeds used in NFACT_PP/probtrackx
  --roi ROI, -r ROI     REQUIRED FOR SURFACE SEEDS: Txt file with ROI(s) paths to restrict seeding to (e.g. medial wall masks).
  -a ALGO, --algo ALGO  What algorithm to run. Options are: NMF (default), or ICA.
  -c COMPONENTS, --components COMPONENTS
                        REQUIRED FOR ICA: Components for the PCA (default is 1000)
  -p PCA_TYPE, --pca_type PCA_TYPE
                        REQUIRED FOR ICA: Type of PCA to do before ICA. Default is PCA which is sckitlearn's PCA. Other option is migp (MELODIC's Incremental Group-PCA dimensionality). This is case insensitive
  -W, --wta             Save winner-takes-all maps
  -z WTA_ZTHR, --wta_zthr WTA_ZTHR
                        Winner-takes-all threshold (default=0.)
  -N, --normalise       Normalises components by zscoring.
  -S, --sign_flip       Don't Sign flip components of ICA
  -O, --overwrite       Overwrite previous file structure
  -n CONFIG, --nfact_config CONFIG
                        Provide config file to change hyperparameters for ICA and NMF. Please see sckit learn documentation for NMF and FASTICA for further details
  -hh, --verbose_help   Prints help message and example usages


Basic NMF with volume seeds usage:
    nfact_decomp --list_of_subjects /absolute path/sub_list \
                 --seeds /absolute path/seeds.txt \
                 --dim 50

Basic NMF usage with surface seeds:
    nfact_decomp --list_of_subjects /absolute path/sub_list \
                 --seeds /absolute path/seeds.txt \
                 --roi /path/to/rois
                 --dim 50

ICA with config file usage:
    nfact_decomp --list_of_subjects /absolute path/sub_list \
                 --seeds /absolute path/seeds.txt \
                 --outdir /absolute path/study_directory \
                 --algo ICA \
                 --nfact_config /path/to/config/file

Advanced ICA Usage:
    nfact_decomp --list_of_subjects /absolute path/sub_list \
                 --seeds /absolute path/seeds.txt \
                 --outdir /absolute path/study_directory \
                 --algo ICA \
                 --migp 1000 \
                 --dim 100 \
                 --normalise \
                 --wta \
                 --wat_zthr 0.5

```
------------------------------------------------------------------------------------------------------------------------------------------

```
_   _ ______   ___   _____  _____  ______ ______
| \ | ||  ___| / _ \ /  __ \|_   _| |  _  \| ___ \
|  \| || |_   / /_\ \| /  \/  | |   | | | || |_/ /
| . ` ||  _|  |  _  || |      | |   | | | ||    /
| |\  || |    | | | || \__/\  | |   | |/ / | |\ \
\_| \_/\_|    \_| |_/ \____/  \_/   |___/  \_| \_|

```

## NFACT Dr

This is the dual regression module of NFACT. Depending on which decompostion method was used depends on which 
dual regression technique will be used. If NMF was used then non-negative least squares regression will be used, if ICA
then it will be standard regression.

### Usage
```
options:
  -h, --help            show this help message and exit
  -l LIST_OF_SUBJECTS, --list_of_subjects LIST_OF_SUBJECTS
                        REQUIRED: Filepath to a list of subjects
  -o OUTDIR, --outdir OUTDIR
                        REQUIRED: Path to output directory
  -a ALGO, --algo ALGO  REQUIRED: Which NFACT algorithm to perform dual regression on
  --seeds SEEDS, -s SEEDS
                        REQUIRED: File of seeds used in NFACT_PP/probtrackx
  --roi ROI, -r ROI     RECOMMENDED FOR SURFACE SEEDS: Txt file with ROI(s) paths to restrict seeding to (e.g. medial wall masks).
  -n NFACT_DECOMP_DIR, --nfact_decomp_dir NFACT_DECOMP_DIR
                        REQUIRED IF NFACT_DECOMP: Filepath to the NFACT_decomp directory. Use this if you have ran NFACT decomp
  -d DECOMP_DIR, --decomp_dir DECOMP_DIR
                        REQUIRED IF NOT NFACT_DECOMP: Filepath to decomposition components. WARNING NFACT decomp expects components to be named in a set way. See documentation for further info.
  -N, --normalise       normalise components by scaling
  -hh, --verbose_help   Prints help message and example usages


Dual regression usage:
    nfact_dr --list_of_subjects /path/to/nfact_config_sublist \
        --seeds /path/to/seeds.txt \
        --nfact_decomp_dir /path/to/nfact_decomp \
        --outdir /path/to/output_directory \
        --algo NMF

ICA Dual regression usage:
    nfact_dr --list_of_subjects /path/to/nfact_config_sublist \
        --seeds /path/to/seeds.txt \
        --nfact_decomp_dir /path/to/nfact_decomp \
        --outdir /path/to/output_directory \
        --algo ICA

Dual regression with roi seeds usage:
    nfact_dr --list_of_subjects /path/to/nfact_config_sublist \
        --seeds /path/to/seeds.txt \
        --nfact_decomp_dir /path/to/nfact_decomp \
        --outdir /path/to/output_directory \
        --roi /path/to/roi.txt \
        --algo NMF
```

nfact_dr is independent from nfact_decomp however, nfact_decomp expects a strict naming convention of files. If nfact_decomp has not been ran then group average files and components must all be in the same folder. Components must be named W_dim* and G_dim* with group average files named coords_for_fdt_matrix2, lookup_tractspace_fdt_matrix2.nii.gz. 

------------------------------------------------------------------------------------------------------------------------------------------

```
 _   _ ______   ___   _____  _____     ___     ____
| \ | ||  ___| / _ \ /  __ \|_   _|   / _ \   / ___|
|  \| || |_   / /_\ \| /  \/  | |    | | | | | |
| . ` ||  _|  |  _  || |      | |    | | | | | |
| |\  || |    | | | || \__/\  | |    | |_| | | |___
\_| \_/\_|    \_| |_/ \____/  \_/     \__\_\  \____|

```
## NFACT Qc

This is a quality control module that creates a number of hitmaps that can be used to check for bias in decomposition.

Each map contains the number of times that voxel/vertex appears in the decomposition. 

## Output:

Prefix:
- hitmap_*.nii.gz: Volume nii component. Components are thresholded by zscoring to remove noise
- hitmap_*_raw.nii.gz: Volume nii component. Components are not thresholded
- mask_*.nii.gz: Volume nii component. Binary mask of thresholded components
- mask_*_raw.nii.gz: Volume nii component. Binary mask of unthresholded components     
- *.gii: Surface gii component. Components are thresholded by zscoring to remove noise
- *_raw.gii: Surface gii component. Components are not thresholded   

## Usage:

```
usage: nfact [-h] [-n NFACT_FOLDER] [-d DIM] [-a ALGO] [-t THRESHOLD] [-O]

options:
  -h, --help            show this help message and exit
  -n NFACT_FOLDER, --nfact_folder NFACT_FOLDER
                        REQUIRED: Path to nfact output folder
  -d DIM, --dim DIM     REQUIRED: Number of dimensions/components
  -a ALGO, --algo ALGO  REQUIRED:What algorithm to qc. Options are: NMF (default), or ICA.
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold value for z scoring the normalised image
  -O, --overwrite       Overwite previous QC

```

------------------------------------------------------------------------------------------------------------------------------------------

```
 _   _______ ___  _____ _____                    __ _
| \ | |  ___/ _ \/  __ \_   _|                  / _(_)
|  \| | |_ / /_\ \ /  \/ | |     ___ ___  _ __ | |_ _  __ _
| . ` |  _||  _  | |     | |    / __/ _ \| '_ \|  _| |/ _` |
| |\  | |  | | | | \__/\ | |   | (_| (_) | | | | | | | (_| |
\_| \_|_|  \_| |_/\____/ \_/    \___\___/|_| |_|_| |_|\__, |
                                                       __/ |
                                                      |___/

```
## NFACT config

NFACT config is a util tool for nfact, that creates a variety of config files to be used in nfact.

NFACT config can create:
1) nfact_config.pipeline overview. This config JSON file is used in the nfact pipeline to have greater control over parameters.  
2) nfact_config.decomp. A config JSON file to control the hyper-parameters of the ICA and NMF functions.
3) nfact_config.sublist. A list of subjects(TXT file) in a folder. 


## Usage:
```
usage: nfact_config [-h] [-C] [-D] [-s SUBJECT_LIST] [-o OUTPUT_DIR]

options:
  -h, --help            show this help message and exit
  -C, --config          Creates a config file for NFACT pipeline
  -D, --decomp_only     Creates a config file for sckitlearn function hyperparameters
  -s SUBJECT_LIST, --subject_list SUBJECT_LIST
                        Creates a subject list from a given directory
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Where to save config file

```
Altering a Boolean value in a JSON is done by giving then everything has to be lower case i.e true, false. It is advised that unless you are familiar with JSON 
files to use a JSON linter to check they are valid. 

### nfact_config_pipeline.config overview

This is the config file for the nfact pipeline. Please check the individual modules for further details on arguments.

```
{
    "global_input": {
        "list_of_subjects": "Required",
        "outdir": "Required",
        "seed": [
            "Required unless file_tree specified"
        ],
        "overwrite": false,
        "pp_skip": false,
        "dr_skip": false,
        "qc_skip": false,
        "folder_name": "nfact"
    },
    "nfact_pp": {
        "file_tree": false,
        "warps": [],
        "bpx_path": false,
        "roi": [],
        "seedref": false,
        "target2": false,
        "nsamples": "1000",
        "mm_res": "2",
        "ptx_options": false,
        "exclusion": false,
        "stop": false,
        "n_cores": false,
        "cluster": false,
        "cluster_queue": "None",
        "cluster_ram": "60",
        "cluster_time": false,
        "cluster_qos": false
    },
    "nfact_decomp": {
        "dim": "Required",
        "roi": false,
        "algo": "NMF",
        "components": "1000",
        "pca_type": "pca",
        "wta": false,
        "wta_zthr": "0.0",
        "normalise": false,
        "sign_flip": true,
        "config": false
    },
    "nfact_dr": {
        "roi": false,
        "normalise": false
    },
    "nfact_qc": {
        "threshold": "2"
    }
}
```

Everything that has says is required must be given. rois, warps and seed must be given in python list format like this
```
"seed": ["l_seed.nii.gz", "r_seed.nii.gz"]
```

### nfact_config_decomp.config 

This is the nfact_config_decomp.config file.

NFACT does its decomposition using sckit-learn's FastICA (https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html#sklearn.decomposition) and NFM (https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html) so any of the hyperparameters of these functions can be altered by changing the values in the JSON file.

```
{
    "ica": {
        "algorithm": "parallel",
        "whiten": "unit-variance",
        "fun": "logcosh",
        "fun_args": null,
        "max_iter": 200,
        "tol": 0.0001,
        "w_init": null,
        "whiten_solver": "svd",
        "random_state": null
    },
    "nmf": {
        "init": null,
        "solver": "cd",
        "beta_loss": "frobenius",
        "tol": 0.0001,
        "max_iter": 200,
        "random_state": null,
        "alpha_W": 0.0,
        "alpha_H": "same",
        "l1_ratio": 0.0,
        "verbose": 0,
        "shuffle": false
    }
}
```

### nfact_config_sublist

NFACT config will attempt to given a directory work out and write to a file all the subjects in that file. Though nfact will try and filter out 
folders that aren't subjects, it isn't perfect so please check the subject list. 

------------------------------------------------------------------------------------------------------------------------------------------

```
 _   _ ______   ___   _____  _____   _____  _     ___  ___
| \ | ||  ___| / _ \ /  __ \|_   _| |  __ \| |    |  \/  |
|  \| || |_   / /_\ \| /  \/  | |   | |  \/| |    | .  . |
| . ` ||  _|  |  _  || |      | |   | | __ | |    | |\/| |
| |\  || |    | | | || \__/\  | |   | |_\ \| |____| |  | |
\_| \_/\_|    \_| |_/ \____/  \_/    \____/\_____/\_|  |_/
```

This is currently a work in progress module. The aim is to support hypothesis testing between groups.
