import random
def rng(num):
    rngstring = ""
    random.seed()
    for i in range(0, num):
        x = random.randint(0, 9)
        rngstring = rngstring + str(x)
    return rngstring