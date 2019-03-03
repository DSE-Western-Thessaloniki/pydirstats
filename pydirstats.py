#!/usr/bin/python3
import os
from optparse import OptionParser


class FSNode:

    def __init__(self, path, filename, isdir=False, parent=None):
        self.__fspath = path
        self.__fname = filename
        self.__parent = parent
        self.__children = []
        self.__attr = os.stat(path+'/'+filename, follow_symlinks=False)
        self.__cache = dict()
        self.__isdir = isdir

    def size(self):
        try:
            return self.__cache['size']
        except KeyError:
            if self.__isdir:
                sz = self.__attr.st_size
                for child in self.__children:
                    sz += child.size()
                self.__cache['size'] = sz
                return sz
            return self.__attr.st_size

    def children(self):
        return self.__children

    def find_children(self):
        path = self.__fspath + '/' + self.__fname
        try:
            with os.scandir(path) as it:
                for entry in it:
                    # print('Found', entry.name, 'dir:',
                    # entry.is_dir(follow_symlinks=False))
                    self.__children.append(FSNode(path, entry.name,
                                                  entry.is_dir(follow_symlinks=False)))
        except PermissionError as e:
            print(e.strerror, ': \'', e.filename, '\'', sep='')

    def clear_cache(self):
        self.__cache = None
        self.__cache = dict()

    def is_dir(self):
        return self.__isdir

    def name(self):
        return self.__fname

    def path(self):
        return self.__fspath


def populatefs(root, verbose):
    global FS
    FS = FSNode(os.path.dirname(root), os.path.basename(root), True)
    FS.find_children()
    tmp = FS.children()
    msg = ''
    while tmp:
        tmp2 = []
        for child in tmp:
            if child.is_dir():
                if verbose:
                    msg = [' '] * len(msg)
                    msg = ''.join(msg)
                    print(msg, end='\r', sep='')
                    lmsg = len('Populating ') + len(child.path()) +\
                        len(child.name()) + 3
                    if lmsg < 80:
                        msg = 'Populating ' + child.path() + child.name() +\
                            '...'
                    else:
                        msg = 'Populating ' + child.path()[:-(lmsg-84)] +\
                            '...' + '/' + child.name() + '...'
                    print(msg, end='\r', sep='')
                child.find_children()
                tmp2.extend(child.children())
        tmp = tmp2
    if verbose:
        msg = [' '] * len(msg)
        msg = ''.join(msg)
        print(msg, end='\r', sep='')


FS = None


def main():
    parser = OptionParser()
    parser.add_option('-d', '--directory', dest='dirname',
                      help='directory to parse', metavar='DIRECTORY')
    parser.add_option('-q', '--quiet', action='store_false', dest='verbose',
                      default=True, help='don\'t print status messages to stdout')
    (options, args) = parser.parse_args()
    if options.dirname is None:
        parser.print_help()
        exit()
    # print('Dirname:', options.dirname)
    # print('Verbose:', options.verbose)

    # Strip trailing slash
    dirstr = options.dirname
    if dirstr[len(dirstr)-1] == '/':
        dirstr = dirstr[:len(dirstr)-1]
    populatefs(dirstr, options.verbose)
    print('Total size:', FS.size())


if __name__ == "__main__":
    main()
