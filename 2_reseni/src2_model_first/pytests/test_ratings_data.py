#!/usr/bin/env python
import pytest
import pandas as pd
import datatest as dt

# Ratings dataset dataset tests
@pytest.fixture(scope="session")
def ratings(pytestconfig):
    return pytestconfig.getoption("ratings")

@pytest.fixture(scope="session")
@dt.working_directory(__file__)
def df(ratings):
    print("Loading ratings dataset...\n")
    return pd.read_csv(ratings, encoding='cp1251', sep=';')

@pytest.mark.mandatory
def test_columns(df):
    dt.validate(
        df.columns,
        {'User-ID', 'ISBN', 'Book-Rating'}
    )
    print("Test columns passed..")

def test_rating_format(df):
    dt.validate(df['Book-Rating'], int)
    print("Test rating format passed...")