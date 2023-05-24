#!/usr/bin/env python
import pytest, warnings
import pandas as pd
import datatest as dt

# Books dataset tests
@pytest.fixture(scope="session")
def books(pytestconfig):
    return pytestconfig.getoption("books")

@pytest.fixture(scope="session")
@dt.working_directory(__file__)
def df(books):
    print("Loading books dataset...\n")
    return pd.read_csv(books, 
                       encoding='cp1251', 
                       sep=';',
                       on_bad_lines='warn',
                       )

@pytest.mark.mandatory
def test_columns(df):
    dt.validate(
        df.columns,
        {'ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L'}
    )
    print("Test columns passed..")

def test_year_format(df):
        is_error = pd.to_numeric(df['Year-Of-Publication'], errors='coerce').isna()
        if len(df[is_error]) > 0:
            warnings.warn(UserWarning("Year format is not correct for some rows.")) #df[is_error]['Year-Of-Publication']
        print("Test format passed...")

    
    
