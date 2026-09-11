from os import listdir
import sys, os
from os.path import isfile, join
import csv
from configparser import ConfigParser

PROYECT_PATH = os.getcwd()
sys.path.insert(0, PROYECT_PATH + "/src/")

config = ConfigParser()
config.read("config.cfg")

from example import *


def test_taxes():
    assert taxes(150, 21) == 181.5 and taxes(100, 11) == 111 and taxes(110, 200) != 25
