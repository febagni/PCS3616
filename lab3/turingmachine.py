# turingmachine.py - implementation of the Turing machine model
#
# Copyright 2014 Jeffrey Finkelstein.
#
# This file is part of turingmachine.
#
# turingmachine is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# turingmachine is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# turingmachine.  If not, see <http://www.gnu.org/licenses/>.
"""Provides an implementation of the Turing machine model."""
import logging
import os.path

# Create and configure the logger which logs debugging information by default.
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(level=logging.DEBUG)

#: Represents a movement of the read/write head of the Turing machine to the
#: left.
L = -1

#: Represents a movement of the read/write head of the Turing machine to the
#: right.
R = +1

#Stores the loaded TM, output and logger state
tm=[None]
output=[None]
logs=[True]


class UnknownSymbol(Exception):
    """This exception is raised when the Turing machine encounters a symbol
    that does not appear in the transition dictionary.

    """
    pass


class UnknownState(Exception):
    """This exception is raised when the Turing machine enters a state that
    does not appear in the transition dictionary.

    """
    pass


class BadSymbol(Exception):
    """This exception is raised when the user attempts to specify a tape
    alphabet that includes strings of length not equal to one.

    """
    pass


class BadFile(Exception):
    """This exception is raised when the file given by the user is 
    inconsistent with the rules for it.

    """
    pass

class NoMachine(Exception):
    """This exception is raised when the user tries to run without having
    loaded any machine.

    """
    pass

def load(file, max_steps=10000):
    '''Import parameters from given file, that has to be in the following
    structure:
    1st line: "ATM"
    2nd line: Any comment you might want
    3rd line: Input alphabet
    4th line: Tape alphabet
    5th line: Number of tapes (must be 1 yet)
    6th line: Number of trails on each tape (must be 1 yet)
    7th line: Number of directions on which the tapes are infinite (must be 2 yet)
    8th line: Initial state
    9th line: Final state
    10th line and beyond: transitions in the following way:
        current state
        symbol read
        next state
        symbol to be written
        direction to move
    last line: "end"
    Comments are made with "//"

    '''
    #Check if file exists, open it and separate lines
    if not os.path.exists(file): raise BadFile("File does not exist.")
    file=open(file, "r")
    file=file.read()
    file=file.split("\n")
    #Create new list removing every comment
    raw=[]
    for line in file:
        i=0
        while i<len(line):
            if line[i]=="/"and line[i+1]=="/":
                raw.append(line[:i])
                break
            i+=1
        if i==len(line): raw.append(line)
    #Create descriptor separating words and removing null strings/lists
    desc=[]
    for line in raw:
        carac=0
        while carac<len(line):
            if line[carac]=="\t": line[carac]=" "
            carac+=1
        desc.append(line.split(" "))
        i=0
        while i<len(desc[-1]):
            if desc[-1][i]=="":
                desc[-1].pop(i)
                i-=1
            i+=1
    line=0
    while line<len(desc):
        if len(desc[line])==0:
            desc.pop(line)
            line-=1
        line+=1
    #Check static values in code and raise exceptions
    if desc[0][0]!="ATM": raise BadFile("First line is wrong.")
    if desc[4][0]!="1": raise BadFile("Number of tapes must be 1.")
    if desc[5][0]!="1": raise BadFile("Number of trails must be 1.")
    if desc[6][0]!="2": raise BadFile("Number of infinite directions must be 2.")
    if desc[-1][0]!="end": raise BadFile("Last line is wrong.")
    #Get the input and tape alphabets
    in_alph=desc[2]
    tp_alph=desc[3]
    #Get initial and final states
    if len(desc[7])>1: raise BadFile("Initial state must be one only thing.")
    ini=desc[7][0]
    if len(desc[8])>1: raise BadFile("Final state must be one only thing.")
    fin=desc[8][0]
    #Remove from escriptor all the preamble and last line
    desc=desc[9:-1]
    #generate transitions dictionary with the remaining lines
    transitions={}
    states=[]
    i=0
    while i<len(desc):
        #Check if the line sintax is correct and raise exceptions
        if len(desc[i])!=5: raise BadFile("Transition "+str(i+1)+" badly formulated.")
        if desc[i][1] not in tp_alph: raise BadFile("All symbols must be declared in input alphabet.")
        if desc[i][3] not in tp_alph: raise BadFile("All symbols must be declared in input alphabet.")
        if desc[i][4]!="R" and desc[i][4]!="L": raise BadFile("Directions must be either R or L.")
        #Add transition
        #If state alredy exist in states list, just add the transition depending on direction
        if desc[i][0] in states: 
            if desc[i][4]=="R":transitions[desc[i][0]][desc[i][1]]=(desc[i][2],desc[i][3],R)
            else:transitions[desc[i][0]][desc[i][1]]=(desc[i][2],desc[i][3],L)
        #Otherwise add state and dictionary for it in transitions and add the transition
        else:
            states.append(desc[i][0])
            transitions[desc[i][0]]={}
            if desc[i][4]=="R":transitions[desc[i][0]][desc[i][1]]=(desc[i][2],desc[i][3],R)
            else:transitions[desc[i][0]][desc[i][1]]=(desc[i][2],desc[i][3],L)
        #If destination state does not exist, create it and it's dictionary in transitions
        if not desc[i][2] in states: 
            states.append(desc[i][2])
            transitions[desc[i][2]]={}
        i+=1
    #Check if initial and final states are in the transitions and raise errors
    if not ini in states: raise BadFile("Initial state must be in transitions.")
    if not fin in states: raise BadFile("Final state must be in transitions")
    #Return the TM class
    tm[0]=TuringMachine(states, in_alph, ini, fin, transitions, max_steps)

def run(string):
    '''Runs the Turing Machine with given string
    '''
    if tm[0]==None: raise NoMachine("You must first load an machine.")
    print(tm[0](string))

def test(io_file):
    '''Test all the cases in given file and return correctness percentage
    '''
    if not os.path.exists(io_file): raise BadFile(io_file+" does not exist.")
    file=open(io_file)
    file=file.read()
    file=file.split("\n")
    line=0
    while line<len(file):
        file[line]=file[line].split(" ")
        item=0
        while item<len(file[line]):
            if file[line][item]=="":
                file[line].pop(item)
                item-=1
            item+=1
        if len(file[line])==0 or file[line][0][0]=="#":
            file.pop(line)
            line-=1
        line+=1
    tests=[]
    for line in file:
        tests.append([line[0], line[2]])
    logs[0]=False
    cont=0
    n=1
    for test in tests:
        res=tm[0](test[0])
        if res:
            string=output[0]
            while string[0]=="B": string=string[1:]
            while string[-1]=="B": string=string[:-1]
            if string==test[1]: 
                cont+=1
                print("test "+str(n)+": "+"\033[92m {}\033[00m" .format("Correct"))
            else:
                print("test "+str(n)+": "+"\033[91m {}\033[00m" .format("Wrong"))
        else:
            print("test "+str(n)+": "+"\033[91m {}\033[00m" .format("Wrong"))
        n+=1
    logs[0]=True
    print(round(cont/len(tests), 2))

class TuringMachine(object):
    """An implementation of the Turing machine model.

    Once instantiated, the Turing machine can be executed by calling it, and it
    can be reset to its initial state by calling :meth:`reset`.

    `states` is a set of states. A "state" can be anything, but usually simple
    integers suffice.

    `initial_state` is the state of the machine before it starts reading
    symbols from an input string. This state must be a member of `states`. When
    :meth:`reset` is called, the state of the machine will be set to this
    state.

    `accept_state` is the state that will cause the machine to halt and accept
    (that is, return ``True``). This set must be a member of `states`.

    `transition` is a two-dimensional dictionary specifying how the
    "configuration" of the machine (that is, the head location, state, and
    string) changes each time it reads from its input string. The dictionary is
    indexed first by state, then by symbol. Each entry in this two-dimensional
    dictionary must be a three-tuple, *(new_state, new_symbol, direction)*,
    where *new_state* is the next state in which the Turing machine will be,
    *new_symbol* is the symbol that will be written in the current location on
    the string, and *direction* is either :data:`L` or :data:`R`, representing
    movement of the head left or right, repectively.

    `max_steps` is the maximum number of steps the machine can walk before
    it is considered infinite loop and returns False

    The transition dictionary need not have an entry for the accept and reject
    states. For example, the accept and reject states need not be in
    `transition`, because the implementation of :meth:`__call__` checks if this
    Turing machine has entered one of these states and immediately halts
    execution.

    Altohugh they would otherwise be necessary in the formal mathematical
    definition of a Turing machine, this class requires the user to specify
    neither the input alphabet nor the tape alphabet.

    """

    def __init__(self, states, in_alph, initial_state, accept_state,
                 transition, max_steps, *args, **kw):
        self.states = states
        self.in_alph=in_alph
        self.accept_state = accept_state
        self.initial_state = initial_state
        self.transition = transition
        self.max_steps=max_steps

    def _log_state(self, string, head_location, current_state):
        """Logs a visual representation of the current head location, state,
        and contents of the tape of this Turing machine.

        For example, if the Turing machine has ``'_010_'`` on its input tape
        (that is, if `string` is ``'_010_'``), is in state ``4``, and has
        read/write head at the location of the ``1`` symbol, this method would
        log the following messages, one line at a time.

            _010_
              ^
              4

        The caret represents the current location of the read/write head, and
        the number beneath it represents the current state of the machine.

        This method should be called from :meth:`__call__`, during the
        execution of the Turing machine on a particular string.

        """
        logger.debug('')
        logger.debug(string)
        logger.debug(' ' * head_location + '^')
        logger.debug(' ' * head_location + str(current_state))

    def __call__(self, string):
        """Runs the computer program specified by this Turing machine on
        `string`.

        `string` must be a Python string whose first and last characters are
        underscores (``'B'``). The underscore represents a blank on the
        theoretical infinite input tape, and denotes the left and right ends of
        the input string.

        The initial head location of the Turing machine is the left-most
        non-blank character of the string.

        Calling this Turing machine executes the program specified by its
        transition function and returns ``True`` if the Turing machine halts
        and accepts and ``False`` if the Turing machine halts and rejects. This
        method may never terminate if the transition function indicates that
        the Turing machine should loop forever.

        """
        #Check if string is valid
        for char in string:
            if not char in self.in_alph: raise UnknownSymbol("String does not correspond to given input alphabet.")
        current_state = self.initial_state
        string="B"+string+"B"
        # We assume that all strings will be input with one blank on the left
        # and one blank on the right, so the head is initially at position 1.
        head_location = 1
        steps=0
        # may loop forever if accept or reject state are never found
        while True:
            # If the head has moved too far to the left or right, add a blank
            # to the current string in the appropriate location. If a blank is
            # added to the left, the head location must be incremented, since
            # the string has now essentially been shifted right by one cell.
            if head_location < 0:
                string = 'B' + string
                head_location += 1
            elif head_location >= len(string):
                string += 'B'
            if logs[0]: self._log_state(string, head_location, current_state)
            # check for accepting or rejecting configurations
            if current_state == self.accept_state:
                output[0]=string
                return True
            if steps>self.max_steps:
                return False
            # for the sake of brevity, rename some verbose variables
            h = head_location
            q = current_state
            s = string[h]
            # if the current_state is not in the transition table, raise error
            if q not in self.transition:
                raise UnknownState('{} is not in transition'
                                   ' dictionary'.format(q))
            # check if the transition table has an entry for the current symbol
            if s not in self.transition[q]:
                return False
            # compute the new configuration from the transition function
            new_state, new_symbol, direction = self.transition[q][s]
            # assert that the symbol to write is a string of length one
            if len(new_symbol) != 1:
                raise BadSymbol('tape alphabet must only include symbols of'
                                ' length 1 ({})'.format(new_symbol))
            # write the specified new symbol to the string; Python strings are
            # immutable, so we must create a new one
            string = string[:h] + new_symbol + string[h + 1:]
            # set the new state and head location
            current_state = new_state
            # direction is either L or R, which are defined to be -1 and +1
            head_location += direction
            steps+=1
        raise Exception('Turing machine somehow halted without accepting or'
                        ' rejecting.')
