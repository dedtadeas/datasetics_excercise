#!/usr/bin/env python
from thefuzz import fuzz

class ModelHandler():
    def __init__(self, model):
        self.model = model
        pass
    
    def get_rec_books(self, bt_in):
        # Return the author name of boothek title
        fuzz_alowance = 80
        
        # Process input
        bt = (bt_in
              .replace(" ", "")
              .replace(".", "")
              .lower()
              )

        # Check for equality
        if bt in self.model.index:
            return self.model.loc[bt, 'recomendations']

        # If not equal, find similar
        df_tmp = self.model.copy()
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
            return self.model.loc[pick_bt[0], 'recomendations']
        else:
            return None
