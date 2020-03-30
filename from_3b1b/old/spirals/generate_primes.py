import numpy as np
import argparse
import json

def primes(n):
    """ Returns  a list of primes < n """
    sieve = [True] * n
    for i in range(3,int(n**0.5)+1,2):
        if sieve[i]:
            sieve[i*i::2*i]=[False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3,n,2) if sieve[i]]

# Argument options
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--maxn", type=int,
                help="maxn: %(default)s)",default=10000)
ap.add_argument("-f", "--filename",
                help="save filename %(default)s)", default="/tmp/input/assets/primes_1e5.json")
args = vars(ap.parse_args())


# Write primes to "saveto" filename
json = str(primes(args["maxn"]))
with open(args['filename'], 'w') as jfile:
    jfile.write(json)
