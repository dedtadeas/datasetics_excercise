#!/usr/bin/env python

import os, requests, pytest
import numpy as np
import pandas as pd

from pathlib import Path
from yaml import load, FullLoader
from zipfile import ZipFile

from entities.model_maker import ModelMaker

# Setting up environment
project_folder = Path(__file__).parent.parent
pytest_dir = project_folder/"pytests"
data_dir = project_folder.parent/"data"

# Load config.yaml file
with open(project_folder/'config.yaml', 'r') as f:
    cfg = load(f, Loader=FullLoader)

class DataManager():
    def __init__(self) -> None:
        self.dataset_path = data_dir/cfg['dataset_file_name']
        self.model_path = data_dir/cfg['model_file_name']
        pass
    
    def clean_data(self):
        ### Clean data ###
        ratings_path = self.raw_data_folder/cfg['book-rating-file-name']
        books_path = self.raw_data_folder/cfg['book-file-name']
        
        # Test datasets using e.g. pytest, TBD: add some custom checks
        pytest.main(["-s", pytest_dir/'test_ratings_data.py', '--ratings', ratings_path])
        pytest.main(["-s", pytest_dir/'test_books_data.py', '--books', books_path])
        
        # Load ratings dataset
        ratings = pd.read_csv(ratings_path,
                            encoding='cp1251',
                            sep=';'
        )
        
        # Load books dataset
        books = pd.read_csv(books_path,
                            encoding='cp1251',
                            sep=';',
                            on_bad_lines='skip', 
                            # parse column Year-Of-Publication as int, if not possible skip row
                            converters={'Year-Of-Publication': lambda x: int(x) if x.isdigit() else np.nan}
        )
                
        # Clean Books
        # Backing up original cols and prepare for search
        backup_cols = ['orig_Book-Author','orig_Book-Title']
        cols = ['Book-Author','Book-Title']
        books[backup_cols] = books[cols]
        for col in cols:
            books[col] = (books[col]
                          .replace("\s+", "", regex = True) # get rid of white spaces
                          .replace("\.", "", regex = True)  # get rid of dots
                          .apply(lambda s: s.lower() if type(s) == str else s) # lowercase
        )
        
        # Do not include rows with missing data
        mask1 = ~(books['Book-Author'].isnull()) 
        mask2 = ~(books['Book-Title'].isnull())
        books = books[mask1 & mask2]
        
        # Create avg rating column
        avg_ratings = (ratings
                               .groupby(['ISBN','User-ID'])['Book-Rating']
                               .mean()
                               .reset_index()
                               .groupby('ISBN')['Book-Rating']
                               .mean()
                               .reset_index()
                               .rename(columns={'Book-Rating': 'AVG-Rating'})
        )
        books = books.merge(avg_ratings, on='ISBN', how='left')
        
        # Clean ratings
        # Check for user-id column type
        mask1 = ~(pd.to_numeric(ratings['User-ID'], errors='coerce').isna())
        # Remove 0 value ratings
        mask2 = (ratings['Book-Rating'] != 0)  # TBD, to be discussed, what does that mean.
        # Check link to books and users
        mask3 = (ratings['ISBN'].isin(set(books['ISBN'])))
        # Apply masks
        ratings = ratings[mask1 & mask2 & mask3]
        
        # Create and save dataset
        dataset = pd.merge(ratings, books, on=['ISBN'], how ='left') 
        dataset.to_csv(self.dataset_path, index = False)
        return
    
    def download_data(self):
        # Download zip
        response = requests.get(cfg['data-url'])
        zip_file_path = data_dir/'data.zip'
        open(zip_file_path, "wb").write(response.content)
        
        # Unzip
        self.raw_data_folder = zip_file_path.parent/'raw'
        with ZipFile(zip_file_path) as zf:
            zf.extractall(self.raw_data_folder)
        os.remove(zip_file_path)
        return 
    
    def get_dataset(self):
        if not self.dataset_path.is_file():
            print('Dataset is missing.\n Downloading the data ... \n')
            self.download_data()
            self.clean_data()
        dataset = pd.read_csv(self.dataset_path)
        return dataset
    
    def get_model(self):
        if not self.model_path.is_file():
            print('Model is missing.\n Model creation ... \n')
            dataset = self.get_dataset()
            ModelMaker(dataset).create_model()
        model = pd.read_csv(self.model_path).set_index('Book-Title')
        return model
    



