# Filetree

This is the folder to put customised filetree.

All filetree files need to be saved as .tree and must contain:
    
    - seed

    - diff2std, std2diff
    
    - bedpostx

NFACT also comes witha HCP downsample filetree. This is used if gii files have been downsampled.
If seed is a surface file then a roi is needed as well. If stoppage and wtstop masks are needed then put:

    - wtstop(number)
    
    - stop(number)
