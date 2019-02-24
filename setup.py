from setuptools import setup

setup(
	name = "multimedia_wrangler",
	packages = ['multimedia_wrangler'],
	version = "1.0.0",
	description = 'This utility scans directories recursively, finds picture and video files, and organizes pictures by EXIF info. Redudant pictures are ignored by hash instead of filename.',
	author = "Elisha Roberson",
	author_email = 'dr.eli.roberson@gmail.com',
	url = 'https://github.com/eroberson/multimedia_wrangler',
	license = 'MIT',
	classifiers=[
	"Development Status :: 5 - Production/Stable",
	"Environment :: Console",
	"Intended Audience :: End Users/Desktop",
	"Intended Audience :: Science/Research",
	"License :: OSI Approved :: MIT License",
	"Topic :: Utilities",
	"Programming Language :: Python :: 2.7",
	"Programming Language :: Python :: 3",
	"Programming Language :: Python :: 3.2",
	"Programming Language :: Python :: 3.3",
	"Programming Language :: Python :: 3.4",
	"Programming Language :: Python :: 3.5",
	"Programming Language :: Python :: 3.6"
	],
	keywords='organizing large picture collections by EXIF information',
	install_requires = ['PIL'],
	entry_points = {'console_scripts':["multimedia_wrangler = multimedia_wrangler.__main__:run"]},
	test_suite = 'nose.collector',
	tests_require = ['nose']
)
