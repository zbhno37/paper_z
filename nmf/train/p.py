#:encoding:utf-8
#!/usr/bin/python

import sys

def readTrainData():
    duplicaset = set()
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        user = line.strip()
        item = sys.stdin.readline().strip()
        score =  float(sys.stdin.readline().strip())
        sys.stdin.readline()
        sys.stdin.readline()

        if (user + "/" + item) in  duplicaset:
            continue
        duplicaset.add(user + "/" + item)

        print '%s\t%s\t%s' % (user, item, score)

if __name__ ==  "__main__":
    readTrainData()

