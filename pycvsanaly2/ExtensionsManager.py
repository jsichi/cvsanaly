# Copyright (C) 2008 LibreSoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

from extensions import get_extension, ExtensionRunError, ExtensionUnknownError
from utils import printerr, printout

class ExtensionException (Exception):
    '''ExtensionException'''

class InvalidExtension (ExtensionException):
    def __init__ (self, name):
        self.name = name

class InvalidDependency (ExtensionException):
    def __init__ (self, name1, name2):
        self.name1 = name1
        self.name2 = name2
        
class ExtensionsManager:

    def __init__ (self, exts, hard_order=False):
        self.exts = {}
        self.hard_order = hard_order
        order = 0
        
        for ext in exts:
            name = ext
            
            if hard_order:
                name = str(order) + name
                order = order + 1
                
            try:
                self.exts[name] = get_extension (ext)
            except ExtensionUnknownError:
                raise InvalidExtension (ext)

            # Add dependencies
            if not hard_order:
                for dep in self.exts[ext].deps:
                    if dep not in self.exts.keys ():
                        try:
                            self.exts[dep] = get_extension (dep)
                        except:
                            raise InvalidDependency (ext, dep)
                        
    def run_extension (self, name, extension, repo, uri, db):
        # Trim off the ordering numeral before printing
        if self.hard_order:
            name = name[1:]
            
        printout ("Executing extension %s", (name,))
        try:
            extension.run (repo, uri, db)
        except ExtensionRunError, e:
            printerr ("Error running extension %s: %s", (name, str (e)))
            return False

        return True
                    
    def run_extensions (self, repo, uri, db):
        done = []
        list = self.exts
   
        for name, extension in [(ext, self.exts[ext] ()) for ext in list]:
            if name in done:
                continue
            done.append (name)

            result = True
            # Run dependencies first
            if not self.hard_order:
                for dep in extension.deps:
                    if dep in done:
                        continue
                    result = self.run_extension (dep, self.exts[dep] (), repo, uri, db)
                    done.append (dep)
                    if not result:
                        break

            if not result:
                printout ("Skipping extension %s since one or more of its dependencies failed", (name,))
                continue
                    
            self.run_extension (name, extension, repo, uri, db)
    
