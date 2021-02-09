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
                        msg = 'Populating ' + child.path() + '/' +\
                            child.name() + '...'
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


def humanreadable(num):
    res = num / 1024
    if res < 1000:
        return "{:.1f}K".format(res)
    res = res / 1024
    if res < 1000:
        return "{:.1f}M".format(res)
    res = res / 1024
    if res < 1000:
        return "{:.1f}G".format(res)
    res = res / 1024
    return "{:.1f}T".format(res)


def getfiles(node):
    fdic = dict()
    for child in node.children():
        if child.is_dir():
            fdic = {**fdic, **getfiles(child)}
        else:
            fdic[child.path() + '/' + child.name()] = child.size()
    return fdic


FS = None


def main():
    parser = OptionParser()
    parser.add_option('-d', '--directory', dest='dirname',
                      help='directory to parse', metavar='DIRECTORY')
    parser.add_option('-c', '--count', dest='results', type="int",
                      help='show at most NUM biggest results', default=10, metavar='NUM')
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
    print('Total size:', humanreadable(FS.size()))
    print('\nTen largest subfolders:')
    folder = dict()
    for child in FS.children():
        if child.is_dir():
            folder[child.name()] = child.size()
    sorted_by_value = sorted(folder.items(), key=lambda kv: kv[1],
                             reverse=True)
    count = 0
    for val in sorted_by_value:
        count += 1
        print(val[0], ': ', humanreadable(val[1]), sep='')
        if count == options.results:
            break
    folder = None
    print('\nTen largest files:')
    files = dict()
    files = getfiles(FS)
    sorted_by_value = sorted(files.items(), key=lambda kv: kv[1],
                             reverse=True)
    count = 0
    for val in sorted_by_value:
        count += 1
        print(val[0], ': ', humanreadable(val[1]), sep='')
        if count == options.results:
            break


if __name__ == "__main__":
    main()
