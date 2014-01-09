Pysync.py
=========

Pysync.py recursively synchronizes the two directories given as arguments, and keeps the file stats intact.

The goal of this script is to be able to keep two huge file trees synchronized, with the origin used as sync master.

With the "-s" option, all files in the destination that are not in the origin are deleted. 
With the "-c" option, nothing is removed.

Some limitations: 
- tested exclusively on Mac OS X 10.9
- ignores all hidden files


