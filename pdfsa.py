'''
Modified by James Edwards
3/9/16

Modified to include the following methods:
generate_haiku              - returns a full haiku, with line syllables = 5, 7, 5
generate_haiku_line         - returns a single line of haiku poetry with a given syllable count
haiku_helper                - recursive function used by the above function that helps generate a line of a haiku
make_syllable_dictionary    - creates a dictionary object from the syllable dictionary text file
'''

import random

class PDFSA:
    '''A class for representing probabilistic deterministic finite state automata.
    
    Several methods have been added to generate sequences of haiku form.'''
    
    def __init__(self, initial_state, final_states, transitions):
        '''__init__ is a special "constructor" function. When creating a new instance of DFSA,
        this function will be called automatically. The user will need to provide the initial state,
        final states, and transitions.
        - transitions should be be a list of (state, label, state, probability) 4-tuples.
        - itial_state should some state in Q.
        - final_states should be a list or set of states in Q.
        Rather than requiring the user to provide sigma and Q, we'll build these sets
        automatically by accumulating all the states and labels mentioned in the transitions
        '''

        # Set instance variables I, F, transitions
        self.I = initial_state
        self.F = final_states
        self.transitions = transitions
        
        # Generate instance variables sigma, Q automatically by looking through the transitions
        self.sigma = set()              # Assume empty alphabet to start
        self.Q = set()                  # Assume no states to start
        for (q1,a,q2,p) in transitions:   
            self.Q.add(q1)              # Add both states mentioned in any transition
            self.Q.add(q2)
            self.sigma.add(a)           # Add the label mentioned in any transition

    def step(self, state, label):
        '''This function returns the unique state we'll get to by being in "state"
        and accepting "label," along with the probability associated with that path.
        If there is no such state, it returns (None, 0.0).
        '''
        for t in self.transitions:
            if (t[0], t[1]) == (state, label):
                return (t[2], t[3])
        return (None, 0.0)

    def probability(self, sequence):
        '''Returns the probability the PDFSA assigns to "sequence" (which can be either
        a list or a string).
        '''
        current_state = self.I      # Start at the beginning
        current_prob = 1.0          # ...with 100% probability

        # Read in the characters one at a time
        for a in sequence:
            current_state, edge_prob = self.step(current_state, a) # Take a step, update what state we're in
            if current_state == None:   # If self.step returned None,
                return 0.0              # ...then the derivation has failed (sequence has 0 probability)
            current_prob *= edge_prob   # Update the probability
            
        # After reading in all the characters, find the probability of stopping at this state
        # (We could also have calculated and stored the stopping probabilities in __init__)
        stop_prob = 1.0
        for t in self.transitions:
            if t[0] == current_state:   # Every time we see an outgoing transition from this final state,
                stop_prob -= t[3]       # subtract that probability from the stopping probability.
        return current_prob * stop_prob # The leftover probability is the probability of stopping

    def generate(self):
        '''Generates some grammatical string by taking a random walk through the FSA.
        Note that this function may return a different result each time it's called.
        '''
        current_state = self.I  # Start at the beginning
        sequence = []           # Start with an empty sequence
        
        while True:
            
            # Find all the edges leaving the current state
            outgoing_edges = []
            for t in self.transitions:
                if t[0] == current_state:
                    outgoing_edges.append(t)
            
            # Pick an outgoing edge (or stopping) using weighted probability.
            # We'll do this by imagining all the outgoing edge probabilities stacked on
            # top of each other, adding to one. We'll pick a random cutoff between 0 and 1,
            # and see which edge in the stack overlaps with that number.
            cutoff = random.random()
            for t in self.transitions:
                if t[0] == current_state:
                    cutoff -= t[3]
                    if cutoff <= 0:
                        next_edge = t
                        sequence.append(next_edge[1])
                        current_state = next_edge[2]
                        break
            # If we went through all the outgoing edges and chose none of them, stop
            else:
                return sequence

    def generate_haiku(self):
        '''Generates a grammatical haiku by taking a random walk through the FSA.
        This walk will be performed three times, with the first and third walks
        requiring a sequence syllable count of 5 and the second walk requiring
        a syllable count of 7. The three sequences will then be printed together.
        Note that this function may return a different result each time it's called.
        '''
        
        ''' Generates a haiku in the form:
        [I, go, to, the beach]
        [It, is, so, much, fun, for, us, all]
        [I, can't, wait, to, go]
        [|==|======|==|]
        '''
        str = " "
        haiku = []
        haiku.append("|==|======|==|")
        haiku.append(str.join(self.generate_haiku_line(5)))
        haiku.append(str.join(self.generate_haiku_line(7)))
        haiku.append(str.join(self.generate_haiku_line(5)))
        return haiku    
        
    def make_syllable_dictionary(self, filename):
        '''Read in a syllable dictionary text file and generate a Python dictionary
        object where the keys correspond to words and the values correspond to
        syllable counts.
        '''       
        # Create an empty dictionary object
        syllables_dict = {}
        # Open the syllable dictionary and store each word and its syllable count
        # in the dictionary
        f = open(filename,"r")
        raw_lines = f.readlines()        
        for line in raw_lines:
            word = ""
            number = 0
            for character in line:
                if character.isalpha():
                    word += character
                elif character.isdigit():
                    number = int(character)
            # Check that the 
            if word != "" and number != 0:
                syllables_dict[word] = number
        return syllables_dict

    def generate_haiku_line(self, syllables_count):
        ''' Generates a line of haiku by calling the recursive
        haiku_helper function.
        '''
        current_state = self.I      # Start at the beginning
        sequence = []              # Start with an empty sequence
        limit = syllables_count     # Required syllables for this line
        
        # Create a dictionary object and fill it with information from our
        # syllabes dictionary text file
        syllables_dict = self.make_syllable_dictionary("syllableDictionary.txt")

        line = self.haiku_helper(syllables_dict, limit, 0, current_state, sequence)
        return line     

    def haiku_helper(self, syllableDict, sylLimit, sylCount, currentState, currentSeq, hasBacktracked = False):
        ''' This method calls itself recursively. It generates a line of haiku 
        with the given number of syllables by generating one word at a time,
        then calling itself again based on the syllable count.
        '''        
        current_state = currentState
        syllableCount= sylCount
        current_sequence = currentSeq
        
        # Find all the edges leaving the current state
        outgoing_edges = []
        for t in self.transitions:
            if t[0] == current_state:
                outgoing_edges.append(t)        
        if outgoing_edges == []:
            # start this line over if a point is reached where there is nowhere to proceed
            return self.haiku_helper(syllableDict, sylLimit, 0, self.I, [])
        cutoff = random.random()
        for t in outgoing_edges:
            if t[0] == current_state:
                cutoff -= t[3]
                #print "the cutoff is currently: " + (str)(cutoff)
                if cutoff <= 0:
                    if t[1] not in syllableDict:
                        syllableDict[t[1]] = 1
                    syllableCount += syllableDict[t[1]]
                    if syllableCount > sylLimit:
                        # Check if it has already had to redo the last syllable 
                        # - if so start over entirely
                        if hasBacktracked == True:
                            return self.haiku_helper(syllableDict, sylLimit, 0, self.I, [])
                        syllableCount -= syllableDict[t[1]]
                        return self.haiku_helper(syllableDict, sylLimit, syllableCount, current_state, current_sequence, hasBacktracked = True)
                    elif syllableCount == sylLimit: 
                        current_sequence.append(t[1])
                        return current_sequence
                    elif syllableCount < sylLimit:
                        next_edge = t
                        current_sequence.append(next_edge[1])
                        current_state = next_edge[2]
                        return self.haiku_helper(syllableDict, sylLimit, syllableCount, current_state, current_sequence, hasBacktracked = False)
            # If we went through all the outgoing edges and chose none of them, try again, because
            # we have not reached the syllable limit yet
        if cutoff > 0:
            return self.haiku_helper(syllableDict, sylLimit, syllableCount, current_state, current_sequence)