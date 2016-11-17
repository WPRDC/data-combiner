import ast
import statistics


def default_measure(*args, **kwargs):
    pass


def count(data, field):
    return len(data)

def mean(data, field):
    d = [row[field] for row in data]
    return statistics.mean(d)

def median(data, field):
    d = [row[field] for row in data if row[field] is not None]
    if not d:
        return "NULL"

    return statistics.median(d)

def mode(data,field):
    d = [row[field] for row in data if row[field] is not None]
    if not d:
        return "NULL"
    return statistics.mode(d)

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
