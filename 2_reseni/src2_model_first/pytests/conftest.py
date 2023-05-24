#!/usr/bin/env python

def pytest_addoption(parser):
    parser.addoption("--ratings", action="store", default="")
    parser.addoption("--books", action="store", default="")
