#!/usr/bin/python3
import os


class FSNode:

    def __init__(self, path, filename, isdir=False, parent=None):
        self.__fspath = path
        self.__fname = filename
        self.__parent = parent
        self.__children = []
        self.__attr = os.stat(path+'/'+filename)
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
        with os.scandir(path) as it:
            for entry in it:
                # print('Found', entry.name, 'dir:',
                # entry.is_dir(follow_symlinks=False))
                self.__children.append(FSNode(path, entry.name,
                                              entry.is_dir(follow_symlinks=False)))

    def clear_cache(self):
        self.__cache = None
        self.__cache = dict()

    def is_dir(self):
        return self.__isdir

    def name(self):
        return self.__fname

    def path(self):
        return self.__fspath


def populatefs(root):
    global FS
    FS = FSNode(os.path.dirname(root), os.path.basename(root), True)
    FS.find_children()
    tmp = FS.children()
    while tmp:
        tmp2 = []
        for child in tmp:
            if child.is_dir():
                print('Populating', child.path() + child.name(), '\r')
                child.find_children()
                tmp2.extend(child.children())
        tmp = tmp2


FS = None

populatefs('/home/oscar/Projects')
print(FS.size())
