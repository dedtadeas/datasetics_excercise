#!/usr/bin/env python

# utf-8 python 3.6
# author: TD
# date: 2023-05-18
# description: Basic script for book recomendation based on correlation of ratings of books
# input datasets: Ratings dataset BX-Book-Ratings.csv, Books dataset BX-Books.csv
# input: book title
# output: recommended books
# usage: python book_rec.py
# requirements: pandas, numpy

# Import
import pandas as pd
import numpy as np
from pathlib import Path
import pytest
# from entities.parser import BookDataParser

# Get parent folder of current script
project_folder = Path(__file__).parent.parent
pytest_dir = Path(__file__).parent/"pytests"
data_folder = project_folder/'data'

#### Data Input #### 
# Get user input
#input_book = input("Enter book title or author you liked: ")  
input_book_name = "The Two Towers (The Lord of the Rings, Part 2)"

# Min number of ratings per book
t = 8

# Datasets
ratings_path = data_folder/'BX-Book-Ratings.csv'
books_path = data_folder/'BX-Books.csv'

#### Data preparation ####
pytest.main(["-s", pytest_dir/'test_ratings_data.py', '--ratings', ratings_path])
pytest.main(["-s", pytest_dir/'test_books_data.py', '--books', books_path])

# data_manager = BookDataParser()
# data_manager.download_files()
# data_manager.load_ratings()
# data_manager.load_books()


# Load ratings dataset
ratings = pd.read_csv(ratings_path,
                      encoding='cp1251',
                      sep=';'
)
mask = ratings['Book-Rating'] != 0
ratings = ratings[mask]

# Load books dataset
books = pd.read_csv(books_path,
                    encoding='cp1251',
                    sep=';',
                    on_bad_lines='warn', 
                    # parse column Year-Of-Publication as int, if not possible skip row
                    converters={'Year-Of-Publication': lambda x: int(x) if x.isdigit() else np.nan}
)
mask = ~(books['Book-Author'].isnull())
books = books[mask]

# Merge datasets
dataset = pd.merge(ratings, books, on=['ISBN'], how='inner')

def get_title_and_author(book_title, df):
    # Return the author name of book title
    # TBD, because we are dealing with user input, the search must be more clever
    # - to lowercase
    # - use fuzzywuzzy package to get best match against df
    mask = df['Book-Title'] == book_title
    # TBD, can be df['Book-Title'].str.contains(book_title, case=False), strip spaces etc.
    if len(x:= df[mask])>0: 
        return [x.iloc[0]['Book-Title'], x.iloc[0]['Book-Author']]
    else: 
        # Handle exception ...
        return

# Get book author
book_title, book_author = get_title_and_author(input_book_name, dataset)

# Get author's readers
mask = dataset['Book-Author'].str.contains(book_author, case=False)
author_readers = set(dataset[mask]['User-ID'])

# Get all (ratings) record of authors readers
# Compute number of ratings per book for all author readers books
# Get book titles with minimal count of t ratings
mask =  dataset['User-ID'].isin(author_readers)
books_to_compare = (dataset[mask]
                        .groupby(['Book-Title'])
                        .size()
                        .loc[lambda x: x>=t]
                        .index
)

# Select ratings for analysis
# Mean User-ID rating per book (i.e. get rid of multiple ratings per user)
cols = ['User-ID', 'Book-Rating', 'Book-Title']
ratings_data_raw = (dataset[cols]
                    .loc[dataset['Book-Title'].isin(books_to_compare)]
                    .groupby(['User-ID', 'Book-Title'])['Book-Rating']
                          .mean()
                          .reset_index()
)

# Create matrix User X BookTitle with rating values
dataset_for_corr = ratings_data_raw.pivot(
    index='User-ID',
    columns='Book-Title',
    values='Book-Rating'
)

# Get avg rating per book
avgrating = (ratings_data_raw[['Book-Title', 'Book-Rating']]
             .groupby('Book-Title')['Book-Rating']
             .mean()
)

# Take out the input book from correlation dataframe
book_data = dataset_for_corr[book_title].dropna()
dataset_of_other_books = dataset_for_corr.loc[book_data.index].drop([book_title], axis=1)

# Corr computation
corr_fellowship = (dataset_of_other_books
             .corrwith(book_data)
             .to_frame()
             .reset_index()
             .merge(avgrating, on='Book-Title', how='left')
             .set_axis(['Book-Title','Corr','Mean_rating'], axis=1)
             .sort_values(by=['Corr','Mean_rating'],ascending=False)
)

print(corr_fellowship.dropna().head(10))
print(corr_fellowship.dropna().tail(10))

