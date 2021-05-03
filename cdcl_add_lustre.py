#!/usr/bin/env python3

# Identify information from Lustre and add them to the schema
# At the moment, use it to store the data into a file for later usage

import sys
import platform
import os
import re
import traceback
import subprocess
from optparse import OptionParser

#from cdcl_info_editor import edit_infos, execute_download

def parse(data):
  # TODO
  for line in data:
    print(line)

parser = OptionParser()
parser.add_option("-j", "--json", dest="json",
                  help="Update this JSON file with the new data", metavar="FILE")
parser.add_option("-f", "--file", dest="filename",
                  help="read data from FILE", metavar="FILE")
parser.add_option("-l", "--lustreFS",
                  dest="lustreFS", default="0",
                  help="The Lustre FS in the schema to fill", metavar="NUMBER")

(options, args) = parser.parse_args()
options.loadFromFile = False

if options.filename != None:
  if os.path.isfile(options.filename):
    # load the data from the file!
    options.loadFromFile = True

if options.loadFromFile: 
  print("Loading from file %s" % options.filename)
  data = open(options.filename, "r")
else:
  # try to fetch the data and store it
  params = [
  "ldlm.namespaces.*.{lru_size,lru_max_age}",
  "llite.*.{max_cached_mb,max_read_ahead_mb,max_read_ahead_per_file_mb}",
  "{mdc,osc}.*.{max_rpcs_in_flight,checksums,max_dirty_mb,max_pages_per_rpc}",
  "llite.*.{lmv,lov}.activeobd",         # number of MDTs/OSTs in filesystem
  "llite.*.{files,kbytes}{free,total}",  # all free and total files and inodes
  "mdc.*.{files,kbytes}{free,total}",    # per-MDT free and total files/inodes
  "osc.*.{files,kbytes}{free,total}",    # per-OST free and total files/inodes
  "{mdc,osc}.*.import"]                  # lots of info about server config
  
  data = subprocess.check_output("lctl get_param debug %s |  sed -e 's/fff[0-9a-f]*/*/'" % " ".join(params), 
	shell = True, encoding='UTF-8')
  if len(data) == 0:
    print("Cannot invoke lctl, trying to use other tools in line")

  data2 = subprocess.check_output("lfs mdts", shell = True, encoding='UTF-8')
  if len(data2) == 0:
    print("Cannot invoke lfs mdts, trying to use other tools in line")
  data = data + "\n" + data2

  data2 = subprocess.check_output("lfs osts", shell = True, encoding='UTF-8')
  if len(data2) == 0:
    print("Cannot invoke lfs osts, trying to use other tools in line")
  data = data + "\n" + data2

  if options.filename:
    print("Saving to file %s" % options.filename)
    file = open(options.filename, 'w')
    file.write(data)
    file.close()
  data = data.split("\n")

parse(data)
