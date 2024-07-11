
``` 
 _   _ ______   ___   _____  _____    
| \ | ||  ___| /   \ /  __ \|_   _|    
|  \| || |_   / /_\ \| /  \/  | |      
|     ||  _|  |  _  || |      | |    
| |\  || |    | | | || \__/\  | |    
\_| \_/\_|    \_| |_/ \____/  \_/ 
```

# NFACT
Non-negative matrix Factorisation of Tractography data

This is a work in progress repo merging NFacT (Shaun Warrington, Ellie Thompson, and Stamatios Sotiropoulos) and ptx_decomp (Saad Jbabdi and Rogier Mars).

Consists of NFACT and NFACT pre-processing (NFACT_PP).  

------------------------------------------------------------------------------------------------------------------------------------------

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



## Input for nfact_preproc

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


 ## NFACT PP input folder 

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


## Usage:

```
 _   _ ______   ___   _____  _____     ______ ______
| \ | ||  ___| /   \ /  __ \|_   _|    | ___ \| ___ \
|  \| || |_   / /_\ \| /  \/  | |      | |_/ /| |_/ /
|     ||  _|  |  _  || |      | |      |  __/ |  __/
| |\  || |    | | | || \__/\  | |      | |    | |
\_| \_/\_|    \_| |_/ \____/  \_/      \_|    \_|


usage: NFACT_PP [-h] -f STUDY_FOLDER -i REF [-l LIST_OF_SUBJECTS] [-b BPX_PATH] [-t TARGET2] [-s SEED [SEED ...]] [-r ROIS [ROIS ...]] [-m MASK] [-w WARPS [WARPS ...]] [-o OUT] [-H] [-g] [-N NSAMPLES] [-R RES]
                [-P PTX_OPTIONS] [-n N_CORES] [-C]

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
                        Path to target image. If not given will create a whole mask
  -s SEED [SEED ...], --seed SEED [SEED ...]
                        The suffixes of the paths leading to the left and right hemisphere cortical seeds (white-grey boundary GIFTI)
  -r ROIS [ROIS ...], --rois ROIS [ROIS ...]
                        The suffixes of the paths leading to the left and right hemisphere medial wall masks (GIFTI)
  -w WARPS [WARPS ...], --warps WARPS [WARPS ...]
                        The suffix of the path leading to the transforms between standard space and diffusion space
  -o OUT, --out OUT     Path to output folder
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

Example Usage:
    Seed surface mode:
           python3 -m NFACT_PP --study_folder /home/mr_robot/subjects
               --list /home/mr_robot/sub_list
               --bpx_path Diffusion.bedpostX
               --seeds L.white.32k_fs_LR.surf.gii R.white.32k_fs_LR.surf.gii
               --rois L.atlasroi.32k_fs_LR.shape.gii  R.atlasroi.32k_fs_LR.shape.gii
               --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz
               --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz
               --gpu --n_cores 3


    Volume surface mode:
            python3 -m NFACT_PP --study_folder /home/mr_robot/subjects
                --list /home/mr_robot/sub_list
                --bpx_path Diffusion.bedpostX
                --seeds L.white.nii.gz R.white.nii.gz
                --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz
                --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz
                --target dlpfc.nii.gz
                --gpu --n_cores 3


    HCP mode:
        python3 -m NFACT_PP --hcp_stream
            --study_folder /home/mr_robot/subjects
            --list /home/mr_robot/sub_list
            --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz
            --gpu --n_cores 3

```