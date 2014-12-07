
import os

DIR_NAMES = [
    "openrcv",
    "openrcv_setup",
    "pandoc_filters",
]


LICENSE = """\
#
# Copyright (c) 2014 Chris Jerdonek. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
"""

def on_path(path):
    with open(path, encoding="utf-8") as f:
        contents = f.read()
    if contents.startswith(LICENSE):
        print("skipping")
        return
    contents = LICENSE + contents
    with open(path, mode="w", encoding="utf-8") as f:
        f.write(contents)

def process_dir(dir_name):
    paths = []
    for dir_path, dirnames, file_names in os.walk(dir_name):
        file_names = (file_name for file_name in file_names if file_name.endswith(".py"))
        for file_name in file_names:
            paths.append(os.path.join(dir_path, file_name))
    sorted(paths)
    for path in paths:
        print("processing: %s" % path)
        on_path(path)


def main():
    for dir_name in DIR_NAMES:
        process_dir(dir_name)


if __name__ == "__main__":
    main()
