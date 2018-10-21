import random
import time


def generate_id(size=1000000000):
    return random.randint(0, size)


def random_str():
    import string
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))


def get_now():
    return time.time()