# Organize tensors into folders by subject name. Operates in current directory!
filename=$1
while read line; do
    # split the line so we can get MRN and mask ids
    split_line=(`echo $line | tr ',' ' '`)
    mrn=${split_line[0]}
    # all elements but the first one
    maskids=( "${split_line[@]:1}" )
    echo Working on subject $mrn
    mkdir $mrn
    # moves all the mask id tensors associated with the current mrn to appropriate folder
    for m in "${maskids[@]}"; do
        mv ${m}_tensor.nii ${mrn}/
    done
done < $filename