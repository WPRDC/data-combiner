import ast
import statistics


def default_measure(*args, **kwargs):
    pass


def count(data):
    return len(data)

def mean(data):
    return statistics.mean(data)

def median(data):
    return statistics.median(data)

def mode(data):
    return statistics.mode(data)

def countif(data, condition):
    n = 0
    for d in data:
        if condition(d) :
            n += 1
    return n

def contains(data, contains):
    if countif(data, contains):
        return True
    else:
        return False