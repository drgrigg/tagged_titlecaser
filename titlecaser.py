#! /usr/bin/env python3

import argparse
import subprocess

def call_SE_titlecase(uncased: str) -> str:
    command = f'se titlecase "{uncased}"'
    output = subprocess.check_output(command, shell=True, encoding='utf-8')
    return output.strip('\n')


def do_case_change(uncased: str, case: str) -> str:
    if case == 'lower':
        return uncased.lower()
    elif case == 'upper':
        return uncased.upper()
    else:
        return call_SE_titlecase(uncased) 


def check_badly_formed(tagged_string) -> bool:
    # we know from earlier in the call stack that there's at least one < char
    # but we need to know if the start of the string is already INSIDE a tag
    right_angle_index = tagged_string.find('>')
    left_angle_index = tagged_string.find('<')
    return (right_angle_index < left_angle_index)  # True if the first right angle is BEFORE the first left angle


def remove_tags(tagged_string:str) -> str:
    # take out the tags by transcribing and omitting them
    # with a well-formed string we could do this more efficiently with a regex, 
    # but this way is more certain in case a string is badly formed, eg 'h3>A TITLE</h3'
    untagged = ''
    in_a_tag = check_badly_formed(tagged_string)
    tagged_index = 0
    while tagged_index < len(tagged_string):
        if not in_a_tag:
            if tagged_string[tagged_index] == '<':
                in_a_tag = True
            else:
                untagged += tagged_string[tagged_index]  # transfer the char
        else: # we're inside a tag
            if tagged_string[tagged_index] == '>':
                in_a_tag = False
        tagged_index += 1
    return untagged


def process_tagged_string(tagged_string:str, case:str):
    untagged = remove_tags(tagged_string)
    cased = do_case_change(uncased=untagged, case=case)
    tagged_index = 0
    untagged_index = 0
    in_a_tag = check_badly_formed(tagged_string)
    outstring = ''
    while tagged_index < len(tagged_string):
        if not in_a_tag:
            if tagged_string[tagged_index] == '<':
                in_a_tag = True
                outstring += '<'
            else:
                outstring += cased[untagged_index]  # transfer the titlecased letter
                untagged_index += 1
        else: # we're inside a tag
            if tagged_string[tagged_index] == '>':
                in_a_tag = False
                outstring += '>'
            else: # we're inside a tag, keep going
                outstring += tagged_string[tagged_index]
        tagged_index += 1
    return outstring


def change_case(input_string: str, case: str):
    if '<' in input_string:  # does it have at least the start of one tag?
        return process_tagged_string(input_string, case) # treat it specially
    else:
        return do_case_change(uncased=input_string, case=case)


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Change case of a string correctly even if it includes tags.')

    # Add the string parameter
    parser.add_argument('input_string', type=str, help='The input string who case we want to change.')

    # option for kind of casing we want to do
    parser.add_argument('--case', choices=['lower', 'upper', 'titlecase'], default='titlecase', help='Desired case (default: titlecase)')

    # Parse the command-line arguments
    args = parser.parse_args()
    case_wanted = args.case

    # Change the case of the input string
    altered_string = change_case(args.input_string, case_wanted)

    # Print the result
    print()
    print(f'{altered_string}')

if __name__ == '__main__':
    main()