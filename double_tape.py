"""
Author: Rhys Michelis
Description:
    This script simulates a 2 tape DTM using the Morphett Turing machine
    format. Annoyingly, the Morphett simulator does not offer a two tape
    simulation, so I made this to make testing easier.

    This is a command line program, and should be called as follows:
    python double_tape.py <tape 1 input> <tape 2 input> <TM encoding file> <Speed>
    
    - tape 1 input and tape 2 input are self explanatory
    - TM encoding file is a Morphett format encoding of a 2 tape DTM
    - Speed is a factor from 0 to 1000, specifying how many miliseconds
    - each transition should take

"""

import sys, time, re, fileinput
"""
The following two functions were created by the COMP2922
teaching staff, and I have taken them and modified them slightly
"""
def getTMCommands(line):
    tokens = line.strip().split()
    if len(line) == 0 or line[0] == ";" or len(tokens) < 8:
        return []
    else:
        return tokens[:8]

"""
Parses TM/PTM (from stdin)
- Return: list of line in the TM.
- Each line is list of strings (length 5): [stateIn, read, write, direction, stateOut]
  (as with Morphitt syntax)
"""
def parseInput(file_handle):
    lines = file_handle.readlines()
    lines = map(lambda x: x.strip(), lines)
    lines = map(getTMCommands, lines)
    lines = [line for line in lines if len(line) > 0]
    return lines

"""
Prints tape in its current state to command line
"""
def print_tape(tape1, tapehead1, tape2, tapehead2, state, on_screen_tape):
    visible_tape1 = tape1[tapehead1 - (on_screen_tape - 1)//2: tapehead1 + (on_screen_tape +1)//2]
    visible_tape2 = tape2[tapehead2 - (on_screen_tape - 1)//2: tapehead2 + (on_screen_tape +1)//2]
    CLR = "\x1B[0K"
    print(" ", end="")
    for i in visible_tape1:
        print(f"{i} ", end="")
    print()
    print(f"{'^': ^{on_screen_tape * 2 + 1}}")
    print(" ", end="")
    for i in visible_tape2:
        print(f"{i} ", end="")
    print()
    print(f"{'^': ^{on_screen_tape * 2 + 1}}")
    print(f"{state: ^{on_screen_tape * 2 + 1}}")

if __name__ == '__main__':

    # Read TM file
    tm_lines = []
    with open(sys.argv[3], "r") as tm_file:
        tm_lines = parseInput(tm_file)

    # Set speed factor
    speed = float(sys.argv[4])/1000

    # Read out tm lines into a more useful format
    tm_struct = dict()
    for line in tm_lines:
        old_state = line[0]
        old_symbol1 = line[1]
        old_symbol2 = line[2]
        old_symbols = tuple([old_symbol1, old_symbol2])
        new_symbol1 = line[3]
        new_symbol2 = line[4]
        direction1 = line[5]
        direction2 = line[6]
        new_state = line[7]

        # Check if this state is in dictionary yet
        if not old_state in tm_struct:
            tm_struct[old_state] = dict()

        # Check if this symbol is in dictionary yet
        if not old_symbols in tm_struct[old_state]:
            tm_struct[old_state][old_symbols] = {
                    'new_symbol1': new_symbol1,
                    'new_symbol2': new_symbol2,
                    'direction1': direction1,
                    'direction2': direction2,
                    'new_state': new_state
                    }

    # How much of the tape do we wish to display on screen
    # Change this value to allow for the depiction of more or less tape
    # Might break if an even number is used? Hopefully not.
    on_screen_tape = 51

    # Get the tape input from the command line
    input_string1 = sys.argv[1]
    input_string2 = sys.argv[2]

    # An array which holds the tape
    tape1 = ['_'] * on_screen_tape * 3
    tape2 = ['_'] * on_screen_tape * 3

    # The starting position of the tapehead
    tape_head1 = (len(tape1) + 1) // 2
    tape_head2 = (len(tape1) + 1) // 2

    # Add input strings to tape
    for i in range(tape_head1, tape_head1 + len(input_string1)):
        tape1[i] = input_string1[i - tape_head1]
    for i in range(tape_head2, tape_head2 + len(input_string2)):
        tape2[i] = input_string2[i - tape_head2]

    # Expected initial state
    state = "0"

    # Print the tape
    print_tape(tape1, tape_head1, tape2, tape_head2, state, on_screen_tape)

    # Go into a loop of executing commands
    while state[:4] != 'halt':
        
        # Figure out what to do in current scenario:
        old_state = state
        old_sym1 = tape1[tape_head1]
        old_sym2 = tape2[tape_head2]

        # Sorry that this is slightly messy and probably not optimised,
        # it goes through and deals with any asterisk rules and parsing
        # out what rule should be used at any given transition
        if old_state in tm_struct:
            if ((old_sym1, old_sym2)) in tm_struct[old_state]:
                new_sym1 = tm_struct[old_state][((old_sym1, old_sym2))]['new_symbol1']
                new_sym2 = tm_struct[old_state][((old_sym1, old_sym2))]['new_symbol2']
                this_dir1 = tm_struct[old_state][((old_sym1, old_sym2))]['direction1']
                this_dir2 = tm_struct[old_state][((old_sym1, old_sym2))]['direction2']
                state = tm_struct[old_state][((old_sym1, old_sym2))]['new_state']
            elif ((old_sym1, '*')) in tm_struct[state]:
                new_sym1 = tm_struct[old_state][((old_sym1, '*'))]['new_symbol1']
                new_sym2 = tm_struct[old_state][((old_sym1, '*'))]['new_symbol2']
                this_dir1 = tm_struct[old_state][((old_sym1, '*'))]['direction1']
                this_dir2 = tm_struct[old_state][((old_sym1, '*'))]['direction2']
                state = tm_struct[old_state][((old_sym1, '*'))]['new_state']
            elif (('*', old_sym2)) in tm_struct[state]:
                new_sym1 = tm_struct[old_state][(('*', old_sym2))]['new_symbol1']
                new_sym2 = tm_struct[old_state][(('*', old_sym2))]['new_symbol2']
                this_dir1 = tm_struct[old_state][(('*', old_sym2))]['direction1']
                this_dir2 = tm_struct[old_state][(('*', old_sym2))]['direction2']
                state = tm_struct[old_state][(('*', old_sym2))]['new_state']
            elif (('*', '*')) in tm_struct[state]:
                new_sym1 = tm_struct[old_state][(('*', '*'))]['new_symbol1']
                new_sym2 = tm_struct[old_state][(('*', '*'))]['new_symbol2']
                this_dir1 = tm_struct[old_state][(('*', '*'))]['direction1']
                this_dir2 = tm_struct[old_state][(('*', '*'))]['direction2']
                state = tm_struct[old_state][(('*', '*'))]['new_state']
            else:
                print(f'TM underspecified: No rule for state {old_state} symbols {old_sym1}, {old_sym2}')
                exit()
        elif '*' in tm_struct:
            if ((old_sym1, old_sym2)) in tm_struct['*']:
                new_sym1 = tm_struct['*'][((old_sym1, old_sym2))]['new_symbol1']
                new_sym2 = tm_struct['*'][((old_sym1, old_sym2))]['new_symbol2']
                this_dir1 = tm_struct['*'][((old_sym1, old_sym2))]['direction1']
                this_dir2 = tm_struct['*'][((old_sym1, old_sym2))]['direction2']
                state = tm_struct['*'][((old_sym1, old_sym2))]['new_state']
            elif ((old_sym1, '*')) in tm_struct['*']:
                new_sym1 = tm_struct['*'][((old_sym1, '*'))]['new_symbol1']
                new_sym2 = tm_struct['*'][((old_sym1, '*'))]['new_symbol2']
                this_dir1 = tm_struct['*'][((old_sym1, '*'))]['direction1']
                this_dir2 = tm_struct['*'][((old_sym1, '*'))]['direction2']
                state = tm_struct['*'][((old_sym1, '*'))]['new_state']
            elif (('*', old_sym2)) in tm_struct['*']:
                new_sym1 = tm_struct['*'][(('*', old_sym2))]['new_symbol1']
                new_sym2 = tm_struct['*'][(('*', old_sym2))]['new_symbol2']
                this_dir1 = tm_struct['*'][(('*', old_sym2))]['direction1']
                this_dir2 = tm_struct['*'][(('*', old_sym2))]['direction2']
                state = tm_struct['*'][(('*', old_sym2))]['new_state']
            elif (('*', '*')) in tm_struct['*']:
                new_sym1 = tm_struct['*'][(('*', '*'))]['new_symbol1']
                new_sym2 = tm_struct['*'][(('*', '*'))]['new_symbol2']
                this_dir1 = tm_struct['*'][(('*', '*'))]['direction1']
                this_dir2 = tm_struct['*'][(('*', '*'))]['direction2']
                state = tm_struct['*'][(('*', '*'))]['new_state']
            else:
                print(f'TM underspecified: No rule for state {old_state} symbols {old_sym1}, {old_sym2}')
                exit()
        else:
            print(f'TM underspecified: No rule for state {old_state} symbols {old_sym1}, {old_sym2}')
            exit()


        # Write new symbol to the tape.
        if new_sym1 != '*':
            tape1[tape_head1] = new_sym1
        if new_sym2 != '*':
            tape2[tape_head2] = new_sym2

        # Decide what move tapehead 1 should make
        if this_dir1 == 'L':
            next_tape_head1 = tape_head1 - 1
        elif this_dir1 == 'R':
            next_tape_head1 = tape_head1 + 1
        else:
            next_tape_head1 = tape_head1

        # Decide what move tapehead 2 should make
        if this_dir2 == 'L':
            next_tape_head2 = tape_head2 - 1
        elif this_dir2 == 'R':
            next_tape_head2 = tape_head2 + 1
        else:
            next_tape_head2 = tape_head2

        # Move tapeheads
        if next_tape_head1 - (on_screen_tape - 1) // 2 < 0:
            tape1 = ['_'] * on_screen_tape + tape1
        elif next_tape_head1 + (on_screen_tape - 1) // 2 >= len(tape1):
            tape1 = tape1 + ['_'] * on_screen_tape
        if next_tape_head2 - (on_screen_tape - 1) // 2 < 0:
            tape2 = ['_'] * on_screen_tape + tape2
        elif next_tape_head2 + (on_screen_tape - 1) // 2 >= len(tape2):
            tape2 = tape2 + ['_'] * on_screen_tape
        tape_head1 = next_tape_head1
        tape_head2 = next_tape_head2

        # Reset command line printing, print tape again
        time.sleep(speed)
        UP = "\x1B[5A"
        print(f'{UP}', end="")
        print_tape(tape1, tape_head1, tape2, tape_head2, state, on_screen_tape)
