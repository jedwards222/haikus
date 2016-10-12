'''
Author: James Edwards
Date: 3/3/2016

This code will train a bigram model from a given training set, and then generate
a haiku (or set of haikus) based on the training set.
'''

from ngrams import *

def train_and_generate(training_set_filename, season):
    '''Trains the model and generates the haiku using methods in the ngrams.py
    and pdfsa.py classes'''
    training_data_set = open_as_haikus(training_set_filename)
    haiku_bigram_model = NgramModel(training_data_set, 2)
    print "|==|======|==|"    
    print "|==|" + season + "|==|"
    print haiku_bigram_model.generate_haiku()
    
print "The following haikus represent the four seasons."
# Write an Autumn themed haiku
train_and_generate("Autumn Training.txt", "Autumn")
# Write a Winter themed haiku
train_and_generate("Winter Training.txt", "Winter")
# Write a Spring themed haiku
train_and_generate("Spring Training.txt", "Spring")
# Write a Summer themed haiku
train_and_generate("Summer Training.txt", "Summer")
