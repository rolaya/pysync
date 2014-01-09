#!/usr/bin/python

# pysync.py


# DEPENDENCIES
import sys,argparse
import os,filecmp,shutil

# DEFAULTS
pysyncMajorVersion = 0
pysyncMinorVersion = 1

# copytree function
def syncTree (src,dst,delete=False,verbose=False,fake=False):
	# compare the directories 
	# remark: we don't touch the hidden files
	dirCmp = filecmp.dircmp(src,dst)
	v = verbose
	# see if we have differences, from origin
	for name in dirCmp.left_only:
		# if it's a hidden file, pass
		if not name[:1] is ".": 
			# if it's a directory, we create it in dst, and launch a syncTree on it
			srcName = os.path.join(src,name)
			dstName = os.path.join(dst,name)
			if os.path.isdir(srcName):
				print "d+ - %s" % dstName
				if not fake:
					os.makedirs(dstName)
					syncTree(srcName,dstName,verbose=v,delete=delete,fake=fake)
			else: 
				# we have a file
				if not fake:
					shutil.copy2(srcName,dstName)
					shutil.copystat(srcName,dstName)
				print "f+ - %s ---> %s" % (srcName,dstName)

	# for the directories we had common, launch the syncTree
	for name in dirCmp.common_dirs:
		if not name[:1] is ".":
			syncTree(os.path.join(src,name),os.path.join(dst,name),verbose=v,delete=delete,fake=fake)

	# for the common files, we compare the stats (date)
	for name in dirCmp.common_files:
		if not name[:1] is ".": 
			srcName = os.path.join(src,name)
			dstName = os.path.join(dst,name)
			# compare the creation date
			if not filecmp.cmp(srcName,dstName):
				# files are not the same, we copy the src to dst
				if not fake:
					os.remove(dstName)
					shutil.copy2(srcName,dstName)
					shutil.copystat(srcName,dstName)
				if v: print "fu - %s ---> %s" % (srcName,dstName)


	# for the directories and files only existing in the destination, if the complete flag is set
	if delete:
		for name in dirCmp.right_only:
			if not name[:1] is ".": 
				dstName = os.path.join(dst,name)
				if os.path.isdir(dstName):
					if not fake:
						shutil.rmtree(dstName)
					if v: print "d- ---x %s" % dstName
				else:
					if not fake: 
						os.remove(dstName)
					if v: print "f- ---x %s" % dstName




# Argparser
argParser = argparse.ArgumentParser(description="pysync.py v%d.%d-- Syncs the file tree of two directories." % (pysyncMajorVersion,pysyncMinorVersion))
parseGroup = argParser.add_mutually_exclusive_group(required=True)
parseGroup.add_argument("-s","--sync",action="store_true",help="Standard sync, origin overwrites destination, deletes surplus files at destination")
parseGroup.add_argument("-c","--complete",action="store_true",help="Completion sync, origin is added to destination, no files are deleted in destination.")
argParser.add_argument("-v","--verbose",action="store_true",help="Print out all actions taken by the script")
argParser.add_argument("-f","--fake",action="store_true",help="Only simulate the actions")
argParser.add_argument("origin",help="The origin directory.")
argParser.add_argument("destination",help="The destination directory.")
args = argParser.parse_args()

# Check if the directories exist and if the destination is writable
if not os.path.exists(args.origin):
	print "Origin directory does not exist."
	sys.exit(1)
if not os.path.exists(args.destination):
	print "Destination directory does not exist."
	sys.exit(1)
elif not os.access(args.destination,os.W_OK):
	print "Destination directory is not writable"
	sys.exit(2)

# let's sync the tree
syncTree(args.origin,args.destination,verbose=args.verbose,delete=args.sync,fake=args.fake)