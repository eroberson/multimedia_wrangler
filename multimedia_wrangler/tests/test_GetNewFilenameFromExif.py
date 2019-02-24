#!/usr/bin/env python

###########
# imports #
###########
import argparse
import hashlib
import datetime
import logging
import os
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import sys

###################################
# import from initialization file #
###################################
from multimedia_wranger import __script_name__, __version__, BufferedReadMd5Hash, GetNewFilenameFromExif, MakeDirIfNotExists, FilenameTestIfExist

def run():
	##################
	# some constants #
	##################
	images = ( "jpg", "jpeg" )
	videos = ( "mp4", "mpeg4", "avi", "mov", "mvi", "3gp" )
	images_with_no_exif = ( "png", "gif", "tif", "tiff", "bmp", "xcf", "psd" )
	
	############################
	# Tracking for file hashes #
	############################
	hash_dict = {}

	#############
	# arg parse #
	#############
	parser = argparse.ArgumentParser( prog=__script_name__, epilog="%s v%s" % ( __script_name__, __version__ ) )
	
	parser.add_argument( "source_directory", help="Directory to walk and find files for organizing" )
	parser.add_argument( "target_directory", help="Directory where files will be moved to for organization" )
	parser.add_argument( "--pic_dir", help = "Name of image subfolder in target_directory", default="pics" )
	parser.add_argument( "--vid_dir", help = "Name of video subfolder in target_directory", default="vids" )
	parser.add_argument( "--noExifDir", help="If image has no Exif, where do we send it?", default="NoExif" )
	parser.add_argument( "--readbuffer", help="Size of the buffer used for hashing. Larger buffers may be faster for large files.", type=int, default = 2 ** 11 )
	
	parser.add_argument( "--dryrun", help="Go through the motions, but don't move anything", default=False, action='store_true' )
	
	parser.add_argument( "--loglevel", choices=[ 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' ], default='INFO' )

	input_args = parser.parse_args()
	
	#################
	# setup logging #
	#################
	logging.basicConfig( format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
	logger = logging.getLogger( __script_name__ )
	logger.setLevel( input_args.loglevel )
	
	#######################################
	# print the relevant options selected #
	#######################################
	opt_string = "Run info"
	opt_string += "%s v%s\n" %( __script_name__, __version__ )
	opt_string += "Source: %s\n" % ( input_args.source_directory )
	opt_string += "Target: %s\n" % ( input_args.target_directory )
	opt_string += "Pic Subdir: %s\n" % ( input_args.pic_dir )
	opt_string += "Vid Subdir: %s\n" % ( input_args.vid_dir )
	opt_string += "No Exif Info Subdir: %s\n" % ( input_args.noExifDir )
	opt_string += "Read buffer for hashing: %s\n" % ( input_args.readbuffer )
	opt_string += "Dryrun? %s" % ( input_args.dryrun )
	
	logger.info( opt_string )
	
	############################
	# Can't read with 0 buffer #
	############################
	assert input_args.readbuffer > 0
	
	#######################################################################
	# normalize the paths to deal with any relative directory shenanigans #
	#######################################################################
	source_directory = os.path.normpath( input_args.source_directory )
	target_directory = os.path.normpath( input_args.target_directory )
	pic_path = os.path.normpath( input_args.pic_dir )
	vid_path = os.path.normpath( input_args.vid_dir )
	
	###########################################################
	# Don't clobber the source directory                      #
	# And yes, sorting in the same directory could be helpful #
	# But to protect pictures for accidents default is no     #
	# Edit with caution                                       #
	###########################################################
	assert source_directory != target_directory
	
	##########################
	# Deal with output paths #
	##########################
	MakeDirIfNotExists( target_directory )
	
	out_pic_path = os.path.join( target_directory, pic_path )
	out_vid_path = os.path.join( target_directory, vid_path )
	
	MakeDirIfNotExists( out_pic_path )
	MakeDirIfNotExists( out_vid_path )
	
	no_exif_path = os.path.join( out_pic_path, input_args.noExifDir )
	
	MakeDirIfNotExists( no_exif_path )
	
	#################################################
	# Build dictionary of hashes for existing files #
	# Keeps us from saving any renamed images if    #
	# another already exists.                       #
	#################################################
	for walking_dir in [ out_pic_path, out_vid_path ]:
		for root, dirs, files in os.walk( walking_dir, topdown=False ):
			for curr_fname in files:
				extension = curr_fname.rstrip().split( "." )[-1].lower()
				
				if extension in images or extension in videos:
					curr_fpath = os.path.join( root, curr_fname )
					
					##########################################
					# edge case - file exists, but is empty. #
					##########################################
					if not os.path.getsize( curr_fpath ) > 0:
						continue
					
					hash_value = BufferedReadMd5Hash( curr_fpath, input_args.readbuffer )
					
					if hash_value in hash_dict:
						err_msg = "Problem! The output directory has two files with the same hash!!!\n"
						err_msg += "Existing file: %s\n" % ( hash_dict[ hash_value ] )
						err_msg += "New file: %s" % ( curr_fpath )
						
						logger.error( err_msg )
						sys.exit( 1 )
					else:
						hash_dict[ hash_value ] = curr_fpath
		
	###############################
	# Walk source directory       #
	# Find all the files          #
	# See if the match vid        #
	#   or pic types.             #
	# Hash them & check if exists #
	# Copy to output based on     #
	# filetype and exif info      #
	###############################
	for root, dirs, files in os.walk( source_directory, topdown=False ):
		for curr_fname in files:
			extension = curr_fname.rstrip().split( "." )[-1].lower()
			
			curr_fpath = os.path.join( root, curr_fname )
			
			#######################################
			# edge case - again, skip empty files #
			#######################################
			if not os.path.getsize( curr_fpath ) > 0:
				continue
			
			logger.debug( "Current file: %s\nExtension: %s\nroot: %s" % ( curr_fname, extension, root ) )
			
			if extension in images:
				hash_value = BufferedReadMd5Hash( curr_fpath, input_args.readbuffer )
				
				if hash_value in hash_dict:
					logger.debug( "Exists, skipping copy" )
					continue
				else:
					hash_dict[ hash_value ] = curr_fpath
					
				image_exif_info = GetNewFilenameFromExif( curr_fpath )
				
				if image_exif_info[0] is None:
					##############################
					# bummer - no exif info      #
					# nothing to do but move it  #
					# with the other image types #
					##############################
					end_string_idx = -1 * ( len( extension ) + 1 )
					name_without_extension = curr_fname[ : end_string_idx ]
					new_file_path = FilenameTestIfExist( no_exif_path, name_without_extension, extension, hash_value, input_args.readbuffer )
					
					if new_file_path is None:
						logger.debug( "Exists, skipping copy" )
						continue	
					
					logger.debug( "No Exif info for picture!\nPath: %s\nNew Name: %s\nHash: %s" % ( curr_fpath, new_file_path, hash_value ) )
					
					if not input_args.dryrun:
						shutil.copy( curr_fpath, new_file_path )
				else:
					###############################################################################
					# Great! with exif info we can pull the DateTimeOriginal or DateTimeDigitized #
					# We will use this to generate an output path                                 #
					# Standard path:                                                              #
					# target_directory --> year --> month --> YYYY-MM-DD-HHMMSS.jpeg              #
					###############################################################################
					out_dir_path = os.path.join( out_pic_path, image_exif_info[1], image_exif_info[2] )
					MakeDirIfNotExists( out_dir_path )
					
					new_file_path = FilenameTestIfExist( out_dir_path, image_exif_info[0], extension, hash_value, input_args.readbuffer )
					
					if new_file_path is None:
						logger.debug( "Exists, skipping copy" )
						continue
					
					logger.debug( "A picture!\nPath: %s\nNew Name: %s\nHash: %s" % ( curr_fpath, new_file_path, hash_value ) )
					
					if not input_args.dryrun:
						shutil.copy( curr_fpath, new_file_path )
				
			elif extension in videos:
				hash_value = BufferedReadMd5Hash( curr_fpath, input_args.readbuffer )
				
				if hash_value in hash_dict:
					logger.debug( "Exists, skipping copy" )
					continue
				
				hash_dict[ hash_value ] = curr_fpath
			
				end_string_idx = -1 * ( len( extension ) + 1 )
				name_without_extension = curr_fname[ : end_string_idx ]
				
				new_file_path = FilenameTestIfExist( out_vid_path, name_without_extension, extension, hash_value, input_args.readbuffer )
				
				if new_file_path is None:
					continue
					# file already exists and has the same hash. Skip items
					
				logger.debug( "A video!\nPath: %s\nNew Name: %s\nHash: %s" % ( curr_fpath, new_file_path, hash_value ) )
					
				if not input_args.dryrun:
					shutil.copy( curr_fpath, new_file_path )
			
			elif extension in images_with_no_exif:
				hash_value = BufferedReadMd5Hash( curr_fpath, input_args.readbuffer )
				
				if hash_value in hash_dict:
					logger.debug( "Exists, skipping copy" )
					continue
				else:
					hash_dict[ hash_value ] = curr_fpath
					
				end_string_idx = -1 * ( len( extension ) + 1 )
				name_without_extension = curr_fname[ : end_string_idx ]
				new_file_path = FilenameTestIfExist( no_exif_path, name_without_extension, extension, hash_value, input_args.readbuffer )
				
				if new_file_path is None:
					logger.debug( "Exists, skipping copy" )
					continue
					
				logger.debug( "No Exif info for picture!\nPath: %s\nNew Name: %s\nHash: %s" % ( curr_fpath, new_file_path, hash_value ) )
					
				if not input_args.dryrun:
					shutil.copy( curr_fpath, new_file_path )

if __name__ == "__main__":
	run()

