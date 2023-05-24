#!/usr/bin/env python

from pathlib import Path
from yaml import load, FullLoader
# from thefuzz import fuzz

project_folder = Path(__file__).parent.parent

# Setting up environment
# Load config.yaml file
with open(project_folder/'config.yaml', 'r') as f:
    cfg = load(f, Loader=FullLoader)


class BookCorrelator():
    def __init__(self, dataset) -> None:
        # Min number of ratings per book
        self.min_rat = cfg['min-ratings']
        self.dataset = dataset
        avg_cols = ['Book-Title', 'AVG-Rating']
        self.book_title_avg_rating = dataset.drop_duplicates(avg_cols[0])[avg_cols]
        pass

    def get_title_author(self, book_title, df):
        # Return the author name of book title
        bt = (book_title
              .replace(" ", "")
              .replace(".", "")
              .lower()
              )

        # Check for equality
        mask = df['Book-Title'] == bt
        if len(x := df[mask]) > 0:
            return bt, x['Book-Author'].to_list()
        else:
            return [None, None]

    def get_correlations(self, input_book_name, dataset):

        # Get book author
        book_title, book_author = self.get_title_author(input_book_name,
                                                        dataset)

        # Get author's readers
        mask = dataset['Book-Author'].isin(book_author)
        author_readers = dataset[mask]['User-ID'].unique()

        # Get all (ratings) record of authors readers
        # Compute number of ratings per book for all author readers books
        # Get book titles with minimal count of t ratings
        mask = dataset['User-ID'].isin(author_readers)
        books_to_compare = (dataset[mask]
                            .groupby(['Book-Title'])
                            .size()
                            .loc[lambda x: x >= self.min_rat]
                            .index
                            )

        # Select ratings for analysis
        # Mean User-ID rating per book (i.e. get rid of multiple ratings per user)
        # Create matrix User X BookTitle with rating values
        cols = ['User-ID', 'Book-Rating', 'Book-Title']
        dataset_for_corr = (dataset[cols]
                            .loc[dataset['Book-Title']
                                 .isin(books_to_compare)]
                            .groupby(['User-ID', 'Book-Title'])['Book-Rating']
                            .mean()
                            .reset_index()
                            .pivot(
                                index='User-ID',
                                columns='Book-Title',
                                values='Book-Rating'
                                )
                            )

        # If there is not enough data for recommendation, return
        if book_title not in dataset_for_corr.columns:
            return

        # Delete input book column from correlation dataframe
        book_data = dataset_for_corr[book_title].dropna()
        dataset_of_other_books = (dataset_for_corr
                                  .loc[book_data.index]
                                  .drop([book_title], axis=1)
                                  )
    
        # Corr computation
        corr_fellowship = (dataset_of_other_books
                           .loc[:, dataset_of_other_books.count() >= 2] # Remove columns with less than two values (i.e. not useful for correlation)
                           .corrwith(book_data)
                           .to_frame()
                           .reset_index()
                           .set_axis(['Book-Title', 'Corr'], axis=1)
                           .merge(self.book_title_avg_rating,
                                  on = 'Book-Title',
                                  how = 'left'
                                  )
                           .sort_values(by=['Corr','AVG-Rating'], ascending=False)
                           .head(10)
                           )

        return corr_fellowship[['Book-Title', 'Corr', 'AVG-Rating']]
