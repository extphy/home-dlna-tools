#!/usr/bin/env python3

import os
import sys
import mutagen.mp4
import logging
import re

filename_re = re.compile('[^\\\\]*(S\\d\\dE\\d\\d)[^\\\\]*\\.mp4$')

class Processor():

   def __init__(self):
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      self.logger = logging.getLogger('retag')
      self.logger.setLevel(logging.DEBUG)
      self.logger.propagate = False;

      coutHandler = logging.StreamHandler(stream=sys.stdout)
      coutHandler.setLevel(logging.DEBUG)
      coutHandler.setFormatter(formatter)
      self.logger.addHandler(coutHandler)

   def process_file(self, mp4_path):
      m = filename_re.match(mp4_path)
      if m == None:
         self.logger.warning("%s doesn't look like an episode", mp4_path)
         return

      tag_title = '\xa9nam'
      manip = mutagen.mp4.MP4(mp4_path)
      title = manip.tags[tag_title] if tag_title in manip.tags else None
      if title != None and len(title) > 0:
         if title[0].startswith(m.group(1)):
            self.logger.debug("%s already tagged", os.path.basename(mp4_path))
            return
         title = [m.group(1) + '.' + title[0].strip(),] +  title[1:]
      else:
         title = [m.group(1),]
      
      self.logger.debug("%s %s",
         os.path.basename(mp4_path), title)

      manip.tags[tag_title] = title

      try:
         manip.save(mp4_path)
      except PermissionError as e:
         self.logger.error("cannot write %s, %s", mp4_path, e)

   def process_dir(self, dir_path):
      if not os.path.isdir(dir_path):
         self.logger.error("%s isn't a directory" % dir_path)
         return

      for dirname, dirnames, filenames in os.walk(dir_path):
         for subdirname in dirnames:
            self.process_dir(os.path.join(dirname, subdirname))

         for filename in filenames:
            if filename.endswith('.mp4'):
               self.process_file(os.path.join(dirname, filename))

def main():

   if len(sys.argv) < 2:
      print("Usage:", sys.argv[0], " <mp4_folder_path>")
      sys.exit(1)

   Processor().process_dir(sys.argv[1])

if __name__ == '__main__':
   main()
