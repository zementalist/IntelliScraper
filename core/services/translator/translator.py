# from deep_translator import GoogleTranslator
# import pandas as pd

# class Translator():

#     def translate_single(text):
#         '''Translate a single text.'''
#         translated = GoogleTranslator(source='auto', target='ar').translate(text=text)
#         return translated
    
#     def translate_batch(df, column_name):
#         '''Translate a target text from file.'''
        
#         for i, text in enumerate(df[column_name]):
#             df['translated'].iloc[i] = GoogleTranslator(source='auto', target='en').translate(text=text)
