import itertools


def sublists(lst):
    temp = []
    for L in range(len(lst) + 1):
        for subset in itertools.combinations(lst, L):
            temp.append(list(subset))
    return temp


def find_non_overlapping_configurations(tasks):
    configurations = sublists(tasks)
    temp = []
    for configuration in configurations:
        n = len(configuration)
        if n == 1:
            temp.append(configuration)
        else:
            flag = False
            for i in range(n - 1):
                for j in range(i + 1, n):
                    if is_overlap(configuration[i], configuration[j]):
                        flag = True
                        break
            if not flag:
                temp.append(configuration)
    return temp


def is_overlap(task_1, task_2):
    """check if there is overal between two tasks with any number of intervals
    """
    flag = False
    for x in task_1:
        for y in task_2:
            if x[0] <= y[1] and y[0] <= x[1]:
                flag = True
    return flag


def find_best_configurations(tasks):
    """ Basic implementation of interval scheduling
    where each task has n >= 1 mutually exclusive intervals
    """
    temp = []
    max_len = len(max(tasks, key=len))
    for x in tasks:
        if len(x) == max_len:
            temp.append(x)
    return temp


if __name__ == '__main__':
    # each task should have non overlapping intervals
    tasks = [[(3, 5), (7, 9)], [(0, 1), (5, 7)], [(0, 3), (9, 10)]]
    configs = find_non_overlapping_configurations(tasks)
    best = find_best_configurations(configs)
    print(best)
