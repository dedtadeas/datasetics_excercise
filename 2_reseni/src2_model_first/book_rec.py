#!/usr/bin/env python

# utf-8 python 3.6
# author: TD
# date: 2023-05-18
# description: Basic script for book recomendation based on correlation of ratings of books
# input datasets: Ratings dataset BX-Book-Ratings.csv, Books dataset BX-Books.csv
# input: book title
# output: recommended books
# usage: python book_rec.py

# Import
from entities.data_manager import DataManager
from entities.model_handler import ModelHandler

if '__main__' == __name__:
    # Load Model
    print('Fetching model...')
    model = DataManager().get_model()
    print('Model fetched...')
    
    # Load Dataset
    dataset = DataManager().get_dataset()
    
    mh = ModelHandler(model)

    while True:
        # Get user input
        input_book_name = input("Enter book title or author you liked: ")
        recommended_books = mh.get_rec_books(input_book_name)
        if recommended_books is not None:
            print(f"Here are some recomended books for you: \n {recommended_books} \n\n")
        else: 
            print("Sorry, we could not find any recommendations for you. Please try again with another book.")
        
