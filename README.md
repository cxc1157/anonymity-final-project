# anonymity-final-project

This repository contains files from my Anonymity and Tor final project.

seq10-50-only200RPs.arff is the initial unpadded dataset.

padded-seq10-50-only200RPs.arff is the dataset after being padded according to the padding scheme in padding.py.

padding.py is the file that parses the initial dataset, adds padding, and creates the new padded dataset.

padding_overhead.txt contains the information about how much padding was added to the original dataset and the percentage of overhead added.

J48-padded.txt, J48-unpadded.txt, kNN-padded.txt, and kNN-unpadded.txt contain the output from running the padded and unpadded datasets through WEKA.

If you wish to run the padding.py program, use the following command:

$ python3 padding.py seq10-50-only200RPs.arff
