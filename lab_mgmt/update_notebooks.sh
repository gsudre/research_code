#!/bin/bash
/usr/bin/rsync -avz --include='*.ipynb' --exclude='*' bw:~/jupyter_notebooks/ncr/ ~/Dropbox/jupyter_notebooks/ncr/
