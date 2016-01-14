import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
import csv
from extract_comment_opinion import DishOpinionExtractor
from extract_enviro_service_comment import EnvirServExtractor

def filter_to_kw(filename):
    dish_extractor = DishOpinionExtractor()
    envir_service_extractor = EnvirServExtractor()
    fout = file('../../paper/data/dianping/comment.keyword', 'w')
    fieldnames = ['_id', 'content', 'shop_id', 'user_id', 'star']
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    with open(filename) as fin:
        reader = csv.DictReader(fin)
        for line in reader:
            if count % 1000 == 0:
                logging.info(count)
            count += 1
            new_comment = ''
            opinion = dish_extractor.extract(line['content'])
            envir_service = envir_service_extractor.extract(line['content'])
            for each in opinion:
                new_comment += ' %s' % ' '.join(each)
            for each in envir_service:
                new_comment += ' %s' % ' '.join(each)
            row = {}
            for key in fieldnames:
                if key != 'content':
                    row[key] = line[key]
            row['content'] = new_comment if new_comment.strip() != '' else line['content']
            writer.writerow(row)

if __name__ == '__main__':
    filter_to_kw('../../paper/data/dianping/comment.mongo')
