from tqdm import tqdm
from time import sleep
from random import random

disable_tqdm = True

if disable_tqdm:
    class tqdm:
        def __init__(self, iterable, *args, **kwargs):
            self.iterable = iterable
            if len(args) > 0:
                print(args[0] + "...")
            elif "desc" in kwargs:
                print(kwargs["desc"] + "...")

        def __iter__(self):
            return iter(self.iterable)


for _ in tqdm(range(100), unit="sleep"):
    sleep(random()*0.04)
