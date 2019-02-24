#!/usr/bin/env python

"""
multimedia_wrangler: a utility for organizing directories of pictures
"""

###########
# imports #
###########
import hashlib
import datetime
import os
from PIL import Image
from PIL.ExifTags import TAGS
import sys

####################
# Version and name #
####################
__script_path__ = sys.argv[0]
__script_name__ = __script_path__.split('/')[-1].split('\\')[-1]
__version__ = '0.0.1'

#############
# functions #
#############
def BufferedReadMd5Hash( fname, byteLimit=2 ** 11 ):
	"""Function to read the MD5 hash of a file, using buffering for large files"""
	
	hasher = hashlib.md5()
	
	with open( fname, 'rb' ) as infile:
		buf = infile.read( byteLimit )
		while( len( buf ) > 0 ):
			hasher.update( buf )
			buf = infile.read( byteLimit )
	return str( hasher.hexdigest() )
	
def GetNewFilenameFromExif( fname ):
	"""For an image file, use EXIF to get DateTimeOriginal, DateTimeDigitized, or DateTime. Extract into new strings used to organize files"""
	try:
		info = Image.open( fname )._getexif()
		exif_dict = {}
		for tag, value in info.items():
			decoded = TAGS.get( tag, tag )
			exif_dict[ decoded ] = value
		
		str_time = None
		if "DateTimeOriginal" in exif_dict:
			str_time = str( exif_dict[ "DateTimeOriginal" ] )
		else:
			str_time = str( exif_dict[ "DateTimeDigitized" ] )
		#else:
		#	str_time = str( exif_dict[ "DateTime" ] )

		as_time = datetime.datetime.strptime( str_time, "%Y:%m:%d %H:%M:%S" )
		
		year_string = datetime.datetime.strftime( as_time, "%Y" )
		month_string = datetime.datetime.strftime( as_time, "%m" )
		tstamp_string = datetime.datetime.strftime( as_time, "%Y-%m-%d_%H%M%S" )
		
		ret_list = [ tstamp_string, year_string, month_string ]
	except KeyError:
		ret_list = [ None, None, None ]
	return ret_list

def MakeDirIfNotExists( dir_path ):
	"""Check for directory and make if it doesn't exist"""
	if not os.path.isdir( dir_path ):
		os.makedirs( dir_path )
		
def FilenameTestIfExist( outpath, base_fname, extension, hash_value, buffer_value = 2 ** 11 ):
	"""Tests if a file exists, and if it does compares hashes to decide if they're different"""
	new_path = os.path.join( outpath, "%s.%s" % ( base_fname, extension ) )
	
	if os.path.isfile( new_path ):
		existing_hash = BufferedReadMd5Hash( new_path, buffer_value )
		
		if existing_hash == hash_value:
			new_path = None
		else:
			idx = 0
			
			while idx < 100:
				idx += 1
				
				if idx < 10:
					idx_string = "0%s" % ( idx )
				else:
					idx_string = "%s" % ( idx )
					
				new_path = os.path.join( outpath, "%s_%s.%s" % ( base_fname, idx_string, extension ) )
				
				if os.path.isfile( new_path ):
					continue
				else:
					break
			else:
				sys.exit( "Couldn't find a filename under 100 iterations" )
				
	return new_path
	
########
# main #
########
if __name__ == "__main__":
	pass
