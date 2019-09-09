#!/usr/bin/python

# pysync.py


# DEPENDENCIES
import sys,argparse
import os,filecmp,shutil

# DEFAULTS
pysyncMajorVersion = 0
pysyncMinorVersion = 2

# GLOBAL FLAGS
verbose = False
fake = False
delete = False
debug = False

# By default, exclude hidden files from copy process
copy_all_files = False

# copyDir function
def copyDir (src,dst):
	# copy the contents of the src directory to the src directory
	dirCmp = filecmp.dircmp(src,dst)

	# for files only in origin:
	for name in dirCmp.left_only:

		if debug:
			print("File unique to source directory: [%s]" % name)

		# pass hidden files
		if copy_all_files or not name[:1] is ".": 
			# get the full path names
			srcName = os.path.join(src,name)
			dstName = os.path.join(dst,name)
			# if it's a dir, create it and launch the copyDir again
			if os.path.isdir(srcName):
				try:
					if not fake: 
						os.makedirs(dstName)
						copyDir(srcName,dstName)
					if verbose: print "d+ %s\t->\t%s" % (srcName,dstName)
				except:
					print "ERROR: can't create or copy directory %s" % dstName
					continue
			# if it's a file, copy the thing and sync the stats
			else:
				try:
					if not fake:
						shutil.copy2(srcName,dstName)
						shutil.copystat(srcName,dstName)
					if verbose: print "c+ %s\t->\t%s " % (srcName,dstName)
				except:
					print "ERROR: can't copy file %s to %s" (srcName,dstName)
					continue

	# if we have common directories, launch the copyDir immediately
	for name in dirCmp.common_dirs:

		if debug:
			print("Common directory: [%s]" % name)

		if copy_all_files or not name[:1] is ".": 
			if not fake: copyDir(os.path.join(src,name),os.path.join(dst,name))

	# if we have files in common, check the source en destination stats
	for name in dirCmp.common_files:
		
		if debug:
			print("Common file: [%s]" % name)
		
		if copy_all_files or not name[:1] is ".":
			srcName = os.path.join(src,name)
			dstName = os.path.join(dst,name)
			if not filecmp.cmp(srcName,dstName):
				try:
					if not fake:

						# The file's contents have changed, replace old file and update its stats.
						os.remove(dstName)
						shutil.copy2(srcName,dstName)
						shutil.copystat(srcName,dstName)

					if verbose: 
						print "u= %s" % dstName
				except:
					print "ERROR: can't update file %s to %s" (srcName,dstName)
					continue

	# if we have stuff in the dst dir that isn't in the src dir, we delete
	if delete:
		for name in dirCmp.right_only:
			if copy_all_files or not name[:1] is ".":
				dstName = os.path.join(dst,name)
				if os.path.isdir(dstName):
					try:
						if not fake: shutil.rmtree(dstName)
						if verbose: print "x- %s" % dstName
					except:
						print "ERROR: can't delete directory %s" % dstName
				else:
					try:
						if not fake: os.remove(dstName)
						if verbose: print "x- %s" % dstName
					except:
						print "ERROR: can't delete file %s" % dstFile




# Argparser
def main():
	global verbose
	global fake
	global delete
	global copy_all_files

	# Set to True to get some additional process flow debug messages.
	global debug

	argParser = argparse.ArgumentParser(description="pysync.py v%d.%d-- Syncs the file tree of two directories." % (pysyncMajorVersion,pysyncMinorVersion))
	
	parseGroup = argParser.add_mutually_exclusive_group(required=True)
	
	parseGroup.add_argument("-s","--sync",action="store_true",help="Standard sync, origin overwrites destination, deletes surplus files at destination")
	parseGroup.add_argument("-c","--complete",action="store_true",help="Completion sync, origin is added to destination, no files are deleted in destination.")
	
	argParser.add_argument("-a","--copy_all_files",action="store_true",help="Copy all files (including hidden files)")
	argParser.add_argument("-v","--verbose",action="store_true",help="Log all actions taken by the script to the command line.")
	argParser.add_argument("-f","--fake",action="store_true",help="Only simulate the actions. Use this with the --verbose option.")
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

	# let's set the globals and sync the tree
	verbose = args.verbose
	delete = args.sync
	fake = args.fake

	# If -or --copy_all_files specified, hidden files will be copied as well.
	copy_all_files = args.copy_all_files

	if debug:
		print "Copy all files (including hidden files): [%s]" % (copy_all_files)
		print "verbose: [%s]" % (verbose)
		print "delete:  [%s]" % (delete)
		print "fake:    [%s]" % (fake)

	copyDir(args.origin,args.destination)

if __name__ == "__main__":
	main()
