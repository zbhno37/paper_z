from collections import defaultdict

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

def dot(a, b):
    res = 0.0
    for i in range(len(a)):
        res += a[i] * b[i]
    return res

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
    dataset = 'arts.txt'
    user_matrix, user_bias = load_nmf_matrix('./out/%s.user' % dataset)
    item_matrix, item_bias = load_nmf_matrix('./out/%s.item' % dataset)
    _matrix, global_bias = load_score_matrix('./train/%s' % dataset)
    print 'global_bias:%s' % global_bias
    for user_id in user_matrix:
        for item_id in item_matrix:
            if _matrix[user_id][item_id] == 0.0: continue
            score = cal_score(user_id, item_id, user_matrix, item_matrix, user_bias, item_bias, global_bias)
            print '%s:%s\t%f\t%f\t%f' % (user_id, item_id, score, _matrix[user_id][item_id], score - _matrix[user_id][item_id])

if __name__ == '__main__':
    main()

