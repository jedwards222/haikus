'''
Author: James Edwards
Date: 3/1/16

This code reads in a phonetic dictionary of English and creates a text file
containing all of the words in the language and the number of syllables in each
word, with each word/syllable count appearing on its own line.
'''

from ngrams import *

def generate_syllable_dictionary(readFile, writeFile):
    '''Given a filename, writes into a text file where each line is a word
    followed by two spaces, then its syllable count.'''
    
    # Open the phonetic dictionary and store each word and its pronunciation
    # in a list
    readLines = open_as_lines(readFile)
    
    # Opens the file that will have the syllable counts stored in it
    toWrite = open(writeFile, "w")    
    
    # Go through each line in the list and count the times a number appears
    # as each number represents a stressed syllable, and thus a distinct syllable
    for line in readLines:
        # Number of syllables and word for each line of dictionary
        currentSyllables = 0
        currentWord = ""
        wordEnd = False
        # Count the appearances of number characters and store the word
        # Two loops because line holds series of words separated by spaces
        for word in line:
            if (word == ''):
                wordEnd = True
            if (wordEnd == False):
                currentWord += word
            else:
                for char in word:
                    if (char in (str(0), str(1),str(2),str(3))):
                        currentSyllables += 1
        # Create the full line to be added to the output text file
        newLine = currentWord
        newLine += "  "
        newLine += str(currentSyllables)
        # Add the current word and the number of syllables as a new line in the text file
        toWrite.write(newLine)
        toWrite.write("\n")
    # Close the files
    toWrite.close
        

'''Run the method, using the CMU Pronouning Dictionary as a source of syllables'''
generate_syllable_dictionary("Pronouncing Dictionary.txt", "syllableDictionary.txt")

