import string 
import random 

def random_suffix(size=5):
    return ''.join([random.choice(string.digits) for i in range(size)])