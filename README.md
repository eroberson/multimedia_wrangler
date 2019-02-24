[![Build Status](https://travis-ci.org/eroberson/multimedia_wrangler.svg?branch=master)](https://travis-ci.org/eroberson/multimedia_wrangler)

# Multimedia wrangler
This is a Python tool for cleaning up directories of images and videos into a structured order. **Important warning** - this tool attempts to avoid clobbering existing files, so the output directory should **not** be the same as th input directory.

Video ExIf extraction is not currently built in, so video files are **not** renamed using image creation information.

Steps
=====
1. Assert the source and output directory are not the same.
2. Make output directory if it doesn't exist.
3. Crawl the output directory taking the md5 hash of every file. This assures that different filenames would result in duplicates.
4. Crawl input directory.
5. For each file, get the md5 hash. If it exists in the hash (either from the output directory or previously encountered in the input), ignore it. If not, add the hash to the dictionary.
6. For new videos, move to a video directory.
7. For new images, check for ExIf information. If none exists, move to an image sub-directory for images with no meta info. If ExIf exists, parse it to get the creation timestamp. Rename the file with the timestamp. If a file with that name exists, appened a number to the timestamp to make it unique. Check if it has been encountered already.

## Installation
Motif scraper is available via pip or GitHub download.
We **HIGHLY** recommend installing in a Python virtual environment.

```bash
pip install multimedia-wrangler
```

Or user install

```bash
pip install --user multimedia-wrangler
```

Or install from GitHub clone.

```bash
git clone https://github.com/eroberson/multimedia_wrangler.git
git checkout vN.N.N # Choose highest version tag instead of vN.N.N

pip install -e .
```

## Usage
```bash
```

