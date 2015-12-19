import csv
import sys
from datetime import datetime

def log(logstr, writer = sys.stdout, inline = False):
    writer.write("%s\t%s%s" % (str(datetime.now()), logstr, '\r' if inline else '\n'))
    writer.flush()

def generate_user_star(filename):
    fout = file('user_star.txt', 'w')
    count = 0
    with open(filename) as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            log(count, inline = True)
            count += 1
            fout.write('%s\t%s\t%s\n' % (row['user_id'], row['shop_id'], row['star']))
    fout.close()
    print ''
    log('Finish')

def main():
    generate_user_star('../../paper/data/comment.mongo')

if __name__ == '__main__':
    main()
