#!/usr/bin/env python

from pathlib import Path
from yaml import load, FullLoader
from tqdm import tqdm
import pandas as pd

from entities.correlator import BookCorrelator

project_folder = Path(__file__).parent.parent

# Setting up environment
# Load config.yaml file
with open(project_folder/'config.yaml', 'r') as f:
    cfg = load(f, Loader=FullLoader)

class ModelMaker():
    def __init__(self, dataset) -> None:
        self.dataset = dataset
        pass

    def create_model(self):
        print('Creating model...')
        # Intialize model
        model = (self.dataset['Book-Title']
                 .drop_duplicates()
                 .sort_values()
                 .to_frame()
                 .assign(recomendations = None)
                 .set_index('Book-Title') 
                 )
        
        # Fill model with correlations
        bc = BookCorrelator(self.dataset)
        def fetch_corrs(self, book_title_list):
            for bt in tqdm(book_title_list):
                yield bt, bc.get_correlations(bt, self.dataset)
        for bt, corr in fetch_corrs(self, model.index):
            if corr is not None:
                model.at[bt,'recomendations'] = corr
        
        # Save model
        model.to_csv(project_folder.parent/'data'/cfg['model_file_name'])
        return
