from collections import defaultdict
import sys
from datetime import datetime

def log(logstr, writer = sys.stdout, inline = False):
    writer.write("%s\t%s%s" % (str(datetime.now()), logstr, '\r' if inline else '\n'))
    writer.flush()

def load_nmf_matrix(filename):
    _matrix = {}
    _bias = defaultdict(float)
    with open(filename) as fin:
        for line in fin:
            arr = line.split('\t')
            nums = arr[1].split(' ')
            _matrix[arr[0]] = [float(x) for x in nums[:-1]]
            _bias[arr[0]] = float(nums[-1])
    return _matrix, _bias

def yield_nmf_matrix(filename):
    with open(filename) as fin:
        for line in fin:
            arr = line.split('\t')
            nums = arr[1].split(' ')
            yield arr[0], [float(x) for x in nums[:-1]], float(nums[-1])

def dot(a, b):
    res = 0.0
    for i in range(len(a)):
        res += a[i] * b[i]
    return res

def cal_score_vector(item_id, user_vector, item_matrix, user_bias, item_bias, global_bias):
    return dot(user_vector, item_matrix[item_id]) + user_bias + item_bias[item_id] + global_bias

def cal_score(user_id, item_id, user_matrix, item_matrix, user_bias, item_bias, global_bias):
    return dot(user_matrix[user_id], item_matrix[item_id]) + user_bias[user_id] + item_bias[item_id] + global_bias

def load_score_matrix(filename):
    # format
    # user_id, item_id, score
    _matrix = defaultdict(lambda: defaultdict(lambda: 0.0))
    total = 0.0
    count = 0
    with open(filename) as fin:
        for line in fin:
            arr = line.split()
            _matrix[arr[0]][arr[1]] = float(arr[2])
            total += float(arr[2])
            count += 1
    return _matrix, total / count

def main():
    fout = file('user_star_res', 'w')
    dataset = 'user_star.txt'
    #log('loading user matrix...')
    #user_matrix, user_bias = load_nmf_matrix('./out/%s.user' % dataset)
    log('loading item matrix...')
    item_matrix, item_bias = load_nmf_matrix('./out/%s.item' % dataset)
    log('loading score matrix...')
    _matrix, global_bias = load_score_matrix('./train/%s' % dataset)
    print 'global_bias:%s' % global_bias
    count = 0
    for user_id, user_vector, user_bias in yield_nmf_matrix('./out/%s.user' % dataset):
        for item_id in item_matrix:
            if user_id not in _matrix or item_id not in _matrix[user_id]: continue
            log(count, inline=True)
            count += 1
            score = cal_score_vector(item_id, user_vector, item_matrix, user_bias, item_bias, global_bias)
            fout.write('%s:%s\t%f\t%f\t%f\n' % (user_id, item_id, score, _matrix[user_id][item_id], score - _matrix[user_id][item_id]))
    fout.close()

def memory_main():
    fout = file('user_star_res', 'w')
    dataset = 'user_star.txt'
    log('loading user matrix...')
    user_matrix, user_bias = load_nmf_matrix('./out/%s.user' % dataset)
    log('loading item matrix...')
    item_matrix, item_bias = load_nmf_matrix('./out/%s.item' % dataset)
    log('loading score matrix...')
    _matrix, global_bias = load_score_matrix('./train/%s' % dataset)
    print 'global_bias:%s' % global_bias
    count = 0
    for user_id in user_matrix:
        for item_id in item_matrix:
            if _matrix[user_id][item_id] == 0.0: continue
            log(count, inline=True)
            count += 1
            score = cal_score(user_id, item_id, user_matrix, item_matrix, user_bias, item_bias, global_bias)
            fout.write('%s:%s\t%f\t%f\t%f\n' % (user_id, item_id, score, _matrix[user_id][item_id], score - _matrix[user_id][item_id]))
    fout.close()
if __name__ == '__main__':
    main()

