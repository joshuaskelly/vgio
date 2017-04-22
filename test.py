import os

for root, dirs, files in os.walk(os.path.expanduser('~/Downloads/qtest1')):
    for name in files:
        fullpath = os.path.join(root, name)
        print(fullpath)
