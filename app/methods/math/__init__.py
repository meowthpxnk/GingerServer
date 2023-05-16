import random

def createIndexMassive(a, b):
    temp = a // b
    delta = a % b
    dump = []
    for idx in range(b):
        dump.append(temp + 1 if delta > 0 else temp)
        delta -= 1
    
    random.shuffle(dump)
    return dump