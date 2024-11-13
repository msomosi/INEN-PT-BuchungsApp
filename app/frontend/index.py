#!/usr/bin/env python3

import os
import psycopg2
from config import load_config

a = 120
b = 150
sum = int(a) + int(b)

print("Content-Type: text/html\n")
print ("Hello World!")
print ("")
print ("The sum is: ", sum)


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


if __name__ == '__main__':
    config = load_config()
    connect(config)


