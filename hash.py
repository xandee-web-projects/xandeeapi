from hashlib import sha256, md5
from .libs import dumps
from random import random

def h(txt, alg=sha256):
    encode = dumps(txt, sort_keys=True).encode()
    hash_f = alg(encode).hexdigest()
    return hash_f

def hsh_a(txt):
    hsh1 = h(txt)
    hsh2 = h(hsh1, md5)
    product = h(hsh1+hsh2)
    return product

def gen_salt():
    rand = random()
    out = h(rand)
    return out

def hash_password(pwd, salt):
    hsh = pwd
    i = 0
    while i != pow(2, 15):
        hsh = hsh_a(hsh+salt)
        i += 1
    return hsh

