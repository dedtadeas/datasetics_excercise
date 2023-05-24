#!/usr/bin/env python

from flask import Flask, render_template, request
import pandas as pd
from thefuzz import fuzz
from io import StringIO

app = Flask(__name__)

model = (pd.read_csv('/home/dedtadeas/mysite/data/model.csv')
            .set_index('Book-Title')
        )

def read_recom_to_html(book_title, md):
    data_str = model.loc[book_title, 'recomendations']
    html = pd.read_csv(StringIO(data_str), delimiter="\s+").to_html()
    return html

@app.route('/', methods=['GET', 'POST'])
def get_recom():
    if request.method == 'POST':
        bt_in = request.form['book_title']

        fuzz_alowance = 80

        # Process input
        bt = (bt_in
              .replace(" ", "")
              .replace(".", "")
              .lower()
              )

        # Check for equality
        if bt in model.index:
            rec_books = read_recom_to_html(bt, model)
            return render_template('index.html', rec_books=rec_books)

        # If not equal, find similar
        df_tmp = model.copy()
        pick_bt = (df_tmp
                   .assign(fuzz_score = (df_tmp
                           .index
                           .to_series()
                           .apply(lambda x: fuzz.ratio(bt, x)))
                           )
                   .loc[lambda x: x['fuzz_score'] > fuzz_alowance]
                   .sort_values('fuzz_score', ascending=False)
                   .index
                   .to_list()
                   )
        if len(pick_bt) > 0 :
            rec_books = rec_books = read_recom_to_html(pick_bt[0], model)
        else:
            rec_books = "<p>Sorry, we do not have enough data in our system for this book. Please try another one.</p>"
        return render_template('index.html', rec_books=rec_books)
    return render_template('index.html')