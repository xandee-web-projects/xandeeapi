from flask.json import dumps, loads
from time import time, sleep
from math import floor
from .hash import hash_password, gen_salt, h
from . import db
from random import randint
