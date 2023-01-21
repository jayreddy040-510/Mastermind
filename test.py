import unittest
import re

x = 4

if re.match(r"^[0-7]{%s}$"%(x), "7341"):
    print("lol")
else:
    print("no")


# bool(re.match(r'^[0-7]{4}$', '7341'))