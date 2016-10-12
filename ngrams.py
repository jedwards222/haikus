'''
Author: Michael Lefkowitz
Date: 2/5/16

This code defines a few functions and a class, NgramModel, to be used
in Lab 2 (Homework 3) of LING 50.01

Modified by James Edwards
3/9/16
Added an "open_as_haikus" method
and a "generate_haiku" method
'''

from pdfsa import PDFSA
from math import log
from collections import defaultdict
import re, string

infinity = float("inf")

# Useful functions for reading in text files as
# corpera of sentences (word sequences)

def open_as_lines(filename):
    '''Given a filename, returns a list of lines, each one a list of words,
    as determined by the position of line breaks.
    Removes caps and punctuation.'''
    f = open(filename,"r")
    raw_lines = f.readlines()
    clean_lines = [line.lower().translate(string.maketrans("-"," "), '.!?;:,"\n') \
                   for line in raw_lines]
    word_lines = [line.split(' ') for line in clean_lines if line != ""]
    word_lines = filter(lambda a: len(a) > 0, word_lines)
    print "Opened",filename,"as a corpus of word ngram counts."
    return word_lines

# Added method, to open the file as haikus, with each set of three lines being 
# added to the list as a single object
def open_as_haikus(filename):
    '''
    Given a filename, returns a list of lists of three lines, each a list of words, 
    as determined by the position of line breaks. Also removes caps and punctuation.
    '''
    f = open(filename,"r")
    raw_lines = f.readlines()
    clean_lines = [line.lower().translate(string.maketrans("-"," "), '.!?;:,"\n') \
                   for line in raw_lines]
    word_lines = [line.split(' ') for line in clean_lines if line != ""]
    word_lines = filter(lambda a: len(a) > 0, word_lines)
    x = 0
    current_haiku = []
    haiku_lines = []
    for line in word_lines:
        x += 1
        if (x%3 != 0):
            current_haiku += line
            # Removed code that would allow for distinguishing liklihoood of words ending lines            
            # current_haiku += "X"
        # If this is the last line of a haiku, add the haiku to the list
        elif (x % 3 == 0):
            haiku_lines.append(current_haiku)
            current_haiku = []
    return haiku_lines


def open_as_sentences(filename):
    '''Given a filename, returns a list of sentences, each a list of words,
    as determined by the position of characters in {!.?}.
    Removes caps and punctuation.'''
    f = open(filename,"r")
    text = f.read().lower()
    sentences = re.split("[!.?]", text)
    word_sentences = [filter(lambda a: a !="'", re.sub("[^\w']", " ",  sentence).split()) \
                      for sentence in sentences]
    word_sentences = filter(lambda a: len(a) > 0, word_sentences)
    print "Opened",filename,"as a corpus of word ngram counts."
    return word_sentences

# Useful function for reading in text files as
# corpera of words (letter sequences)

def open_as_words(filename):
    '''Given a filename, returns a list of words, each one a string,
    as determined by the position of spaces and new lines.
    Ignores caps and punctuation.'''
    f = open(filename,"r")
    words = f.read().lower().translate(string.maketrans("-\n","  "), '.!?;:,()"\t').split()
    words = filter(lambda a: len(a) > 0, words)
    print "Opened",filename,"as a corpus of letter ngram counts."
    return words

#################################
# Defining the NgramModel class #
#################################
class NgramModel:
    '''A class for representing an ngram model'''
    
    def __init__(self, corpus, n, smoothing=0):
        '''Corpus should be a list of lists, or a list of strings (which will be treated as
        character lists). n is the size of ngrams to be used. Smoothing is the degree
        of laplace smoothing to be used (0.0 for no smoothing, 1 for a moderate amount).
        '''
        
        # Set instance variables I, F, transitions
        self.n = n
        self.smoothing = smoothing
        self.letter_grams = type(corpus[0]) is str

        # Get sigma
        self.sigma = set()
        for sequence in corpus:
            for a in sequence:
                self.sigma.add(a)
        
        # Pad the corpus with start and end symbols (^ $ for letters, <s> </s> for words).
        self.corpus = []
        if self.letter_grams:
            self.startpad, self.endpad = '^' * (self.n-1), '$'
        else:
            self.startpad, self.endpad = ['<s>'] * (self.n-1), ['</s>']
        for seq in corpus:
            self.corpus.append(self.startpad + seq + self.endpad)
        
        # Get ngram counts, and n-1 gram counts by cycling through each sequence
        self.ngram_counts = defaultdict(int)
        self.n1gram_counts = defaultdict(int)
        for sequence in self.corpus:
            
            # Get ngram counts, n-1 gram counts
            for i in range(len(sequence) - self.n + 1):
                ngram = tuple(sequence[i:i+n])
                if ngram not in self.ngram_counts:
                    self.ngram_counts[ngram] = 0
                self.ngram_counts[ngram] += 1
                
                n1gram = tuple(sequence[i:i+n-1])
                if n1gram not in self.n1gram_counts:
                    self.n1gram_counts[n1gram] = 0
                self.n1gram_counts[n1gram] += 1

        # Create a PDFSA for generation and probability calculation
        I = tuple(self.startpad)
        F = []
        transitions = []
        for ngram in self.ngram_counts:
            q1 = ngram[:-1]
            q2 = ngram[1:]
            label = ngram[-1]
            if label == self.endpad[0]:
                F.append(q1)
            else:
                prob = self.ngram_counts[ngram] * 1.0 / self.n1gram_counts[q1]
                transitions.append((q1,label,q2,prob))

        self.fsa = PDFSA(I, F, transitions)

    def generate(self):
        '''Probabalistically generates some sequence given this ngram
        language model, using its build-in pfsa.'''
        sequence = self.fsa.generate()
        
        # Make it prettier to read by converting lists to strings, with spaces if needed
        seperator = "" if self.letter_grams else " "
        return seperator.join(sequence)
    
    def generate_haiku(self):
        '''Probabalistically generates some haiku given this ngram
        language model, using its build-in pfsa.'''
        sequence = self.fsa.generate_haiku()
        
        # Make it prettier to read by converting lists to strings, with spaces if needed
        seperator = "\n"
        return seperator.join(sequence)    
    
    def probability(self, sequence, smoothing=0.0, novel_words=0):
        '''Returns the probability of a sequence in this language model.
        setting smoothing higher than 0.0 applies laplace smoothing.
        new_words should be set to the number of expected novel words (not
        observed in the training data) in the test set or other application
        '''
        prob = 1.0
        seq = self.startpad + sequence + self.endpad
        for i in range(len(sequence)+1):
            ngram = tuple(seq[i:i+self.n])
            n1gram = tuple(seq[i:i+self.n-1])
            V = len(self.sigma) + novel_words
            if self.ngram_counts[ngram] + smoothing == 0:
                # print "missing", ngram
                return 0.0
            prob *= (self.ngram_counts[ngram] + smoothing * 1.0) \
                    / (self.n1gram_counts[n1gram] + smoothing * V)
        return prob

    def log_probability_of_test_set(self, test_corpus, smoothing=0.0):
        '''returns the log of the product of the probabilities of all the
        sequences in the new_corpus. Note that since the probability is between
        0 and 1, the log probability will always be a negative number (or at
        most 0). A more negative number means a more unlikely corpus.
        '''
        novel_words = set().union(*test_corpus).difference(self.sigma)
        log_prob = 0
        for seq in test_corpus:
            prob = self.probability(seq, smoothing, len(novel_words))
            if prob == 0:
                return -infinity
            log_prob += log(prob)
        return log_prob

    lpots = log_probability_of_test_set # ...because "log_probability_of_test_set" is a pain to type

