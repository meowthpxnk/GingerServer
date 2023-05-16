import random
import string

def getRandomString(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def generateCookieString():
    return getRandomString(64)