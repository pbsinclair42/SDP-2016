#!/usr/bin/env python2.7
import json
import functools

def read_json(file):
    with open(file, "r") as f:
        return json.loads(f.read())

# https://mathieularose.com/function-composition-in-python/#solution
def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)
