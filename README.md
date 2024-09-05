# NFACT

*This is a work in progress repo merging NFacT (Shaun Warrington, Ellie Thompson, and Stamatios Sotiropoulos) and ptx_decomp (Saad Jbabdi and Rogier Mars).*

## What is NFACT
NFACT (Non-negative matrix Factorisation of Tractography data) is a set of modules (as well as an end to end pipeline) that decomposes 
tractography data using NMF/ICA.

It consists of three "main" decomposition modules:
    
    - nfact_pp (Pre-process data for decomposition)
    
    - nfact_decomp (Decomposes a single or average group matrix using NMF or ICA)
    
    - nfact_dr (Dual regression on group matrix)

as well as two axillary "modules":
    
    - nfact_config (creates config files for the pipeline and changing any hyperparameters)
    
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
--outdir /absolute path /save directory \
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
Pre-processing of tractgraphy data for decomposition with NFacT (Non-negative matrix Factorisation of Tractography data)

Under the hood NFACT PP is probtrackx2 omatrix2 option to get a seed by target connectivity matrix 

### Input for nfact_preproc

Required before runing NFACT PP:
    - crossing-fibre diffusion modelled data (bedpostX)
    - Seeds (either surfaces or volumes)

NFACT PP has three streams, surface seed mode, volume stream mode and HCP stream.

Required input:
    - Study folder
    - Standard space image

Input needed for HCP mode:
    - HCP folder structure

Input needed for both surface and volume mode:
    - Warps
    - bpx folder name
   
Input for surface seed mode:
    - Seeds as surface
    - ROIs as surfaces
    
Input needed for volume mode:
    - Seeds as volume

Optional inputs:
    - list of subjects file. If this isn't provided then NFACT PP will try from the study folder to get list of subjects
    - Target2.nii.gz. If not given then will create a whole brain mask
    - To run on GPU 
    - To run in parallel or on cluster
    - Other ptx options


 ### NFACT PP input folder 

An example set up

```
/home/study1
    ├── ptx_options.txt                                  - An optional txt file with additional ptx options
    ├── list_of_subject.txt                              - An optional list of subjects file with full path to subjects
    ├── subject-01
    │       ├── dmri.bedpostx                            - the bedpostx directory          
    │       ├── std2diff.nii.gz diff2std.nii.gz          - standard to diffusion warp (and visa versa)
    │       ├── seeds.gii/.nii                           - the seed files
    |       ├── target.nii.gz                            - the target file        
    │       └── rois.gii                                 - the left and right medial wall files
    ├── subject-02
    │       ├── dmri.bedpostx                            - the bedpostx directory          
    │       ├── std2diff.nii.gz diff2std.nii.gz          - standard to diffusion warp (and visa versa)
    │       ├── seeds.gii/.nii                           - the seed files
    |       ├── target.nii.gz                            - the target file        
    │       └── rois.gii                                 - the left and right medial wall files
    └── subject-03                 
    │       ├── dmri.bedpostx                            - the bedpostx directory          
    │       ├── std2diff.nii.gz diff2std.nii.gz          - standard to diffusion warp (and visa versa)
    │       ├── seeds.gii/.nii                           - the seed files
    |       ├── target.nii.gz                            - the target file        
    │       └── rois.gii                                 - the left and right medial wall files
```



### Usage:

```
usage: nfact_pp [-h] -f STUDY_FOLDER -i REF [-l LIST_OF_SUBJECTS] [-b BPX_PATH] [-t TARGET2] [-s SEED [SEED ...]] [-r ROIS [ROIS ...]] [-w WARPS [WARPS ...]] [-o OUT] [-H] [-g] [-N NSAMPLES] [-R RES] [-P PTX_OPTIONS] [-n N_CORES] [-C] [-D] [-O]

options:
  -h, --help            show this help message and exit
  -f STUDY_FOLDER, --study_folder STUDY_FOLDER
                        REQUIRED Study folder containing sub directories of participants.
  -i REF, --image_standard_space REF
                        REQUIRED Standard space reference image
  -l LIST_OF_SUBJECTS, --list_of_subjects LIST_OF_SUBJECTS
                        A list of subjects in text form. If not provided NFACT PP will use all subjects in the study folder. All subjects need full file path to subjects directory
  -b BPX_PATH, --bpx BPX_PATH
                        Name of Diffusion.bedpostX directory
  -t TARGET2, --target TARGET2
                        Path to target image. If not given will create a whole mask from reference image
  -s SEED [SEED ...], --seed SEED [SEED ...]
                        The suffixes of the paths leading to the left and right hemisphere cortical seeds (white-grey boundary GIFTI)
  -r ROIS [ROIS ...], --rois ROIS [ROIS ...]
                        The suffixes of the paths leading to the left and right hemisphere medial wall masks (GIFTI)
  -w WARPS [WARPS ...], --warps WARPS [WARPS ...]
                        The suffix of the path leading to the transforms between standard space and diffusion space
  -o OUT, --out OUT     Name of folder to save results into. Default is nfact_pp
  -H, --hcp_stream      HCP stream option. Will search through HCP folder structure for L/R white.32k_fs_LR.surf.gii and ROIs. Then performs suface seed stream
  -g, --gpu             Use GPU version
  -N NSAMPLES, --nsamples NSAMPLES
                        Number of samples per seed used in tractography (default = 1000)
  -R RES, --res RES     Resolution of NMF volume components (Default = 2 mm)
  -P PTX_OPTIONS, --ptx_options PTX_OPTIONS
                        Path to ptx_options file for additional options
  -n N_CORES, --n_cores N_CORES
                        If should parallel process and with how many cores
  -C, --cluster         Run on cluster
  -D, --dont_log        Run on cluster
  -O, --overwrite       Overwrite previous file structure

Example Usage:
    Seed surface mode:
           nfact_pp --study_folder /home/mr_robot/subjects
               --list /home/mr_robot/sub_list
               --bpx_path Diffusion.bedpostX
               --seeds L.white.32k_fs_LR.surf.gii R.white.32k_fs_LR.surf.gii
               --rois L.atlasroi.32k_fs_LR.shape.gii  R.atlasroi.32k_fs_LR.shape.gii
               --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz
               --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz
               --gpu --n_cores 3


    Volume surface mode:
            nfact_pp --study_folder /home/mr_robot/subjects
                --list /home/mr_robot/sub_list
                --bpx_path Diffusion.bedpostX
                --seeds L.white.nii.gz R.white.nii.gz
                --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz
                --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz
                --target dlpfc.nii.gz
                --gpu --n_cores 3


    HCP mode:
        nfact_pp --hcp_stream
            --study_folder /home/mr_robot/subjects
            --list /home/mr_robot/for_axon/nfact_dev/sub_list
            --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz
            --gpu --n_cores 3
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
usage: nfact [-h] [-p PTXDIR [PTXDIR ...]] [-l LIST_OF_SUBJECTS] [-o OUTDIR] [-d DIM] [--seeds SEEDS] [-m MIGP] [-a ALGO] [-w] [-z WTA_ZTHR] [-N] [-S] [-O] [-c CONFIG] [-C SAVE_GREY_AS_CIFIT]

options:
  -h, --help            show this help message and exit
  -p PTXDIR [PTXDIR ...], --ptxdir PTXDIR [PTXDIR ...]
                        List of file paths to probtrackx directories. If not provided will then --list_ofsubjects must be provided
  -l LIST_OF_SUBJECTS, --list_of_subjects LIST_OF_SUBJECTS
                        Filepath to a list of subjects. If not given then --ptxdir must be directories.
  -o OUTDIR, --outdir OUTDIR
                        Path to output folder
  -d DIM, --dim DIM     Number of dimensions/components
  --seeds SEEDS, -s SEEDS
                        File of seeds used in NFACT_PP/probtrackx
  -m MIGP, --migp MIGP  MELODIC's Incremental Group-PCA dimensionality (default is 1000)
  -a ALGO, --algo ALGO  What algorithm to run. Options are: ICA (default), or NMF.
  -w, --wta             Save winner-takes-all maps
  -z WTA_ZTHR, --wta_zthr WTA_ZTHR
                        Winner-takes-all threshold (default=0.)
  -N, --normalise       normalise components by scaling
  -S, --sign_flip       sign flip components
  -O, --overwrite       Overwrite previous file structure. Useful if wanting to perform multiple GLMs or ICA and NFM
  -c CONFIG, --config CONFIG
                        Provide config file to change hyperparameters for ICA and NFM. Please see sckit learn documentation for NFM and FASTICA for further details

```

An example call
```
nfact_decomp --list_of_subjects /absolute path/sub_list \
          --seeds /absolute path/seeds.txt \
          --outdir /absolute path/study_directory \
             --algo ICA \
             --migp 1000 \
             --dim 100 --normalise --wta –sign_flip \

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
usage: nfact_dr [-h] [-p PTXDIR [PTXDIR ...]] [-l LIST_OF_SUBJECTS] [-n NFACT_DIR] [-a ALGO] [--seeds SEEDS] [-N]

options:
  -h, --help            show this help message and exit
  -p PTXDIR [PTXDIR ...], --ptxdir PTXDIR [PTXDIR ...]
                        List of file paths to probtrackx directories. If not provided will then --list_ofsubjects must be provided
  -l LIST_OF_SUBJECTS, --list_of_subjects LIST_OF_SUBJECTS
                        Filepath to a list of subjects. If not given then --ptxdir must be directories.
  -n NFACT_DIR, --nfact_dir NFACT_DIR
                        REQUIRED: Path to NFACT directory
  -a ALGO, --algo ALGO  REQUIRED: Which NFACT algorithm to perform dual regression on
  --seeds SEEDS, -s SEEDS
                        REQUIRED: File of seeds used in NFACT_PP/probtrackx
  -N, --normalise       normalise components by scaling

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

NFACT config creates a json file of the available hyper parameters for the ICA and NMF functions. This json file can then be edited and fed into
NFACT to change the hyperparameters of the FastICA and NMF functions.

NFACT does its decomposition using sckit learn's FastICA (https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html#sklearn.decomposition) 
and NFM (https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html) so any of the hyperparameters of these functions can be altered.

## Usage:
```

usage: nfact_config [-h] [-o OUTPUT_DIR]

options:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Where to save config file

```
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