#! /usr/bin/env python3

import argparse
import regex

def call_SE_titlecase(astring) -> str:
    # this is of course just a dummy, we'd call the real SE titlecase function here
    return astring.title()

def check_badly_formed(tagged_string) -> bool:
    # we know from earlier in the call stack that there's at least one < char
    # but we need to know if the start of the string is already INSIDE a tag
    right_angle_index = tagged_string.find('>')
    left_angle_index = tagged_string.find('<')
    return (right_angle_index < left_angle_index)  # True if the first right angle is BEFORE the first left angle

def remove_tags(tagged_string) -> str:
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

def process_tagged_string(tagged_string):
    untagged = remove_tags(tagged_string)
    titled = call_SE_titlecase(untagged)
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
                outstring += titled[untagged_index]  # transfer the titlecased letter
                untagged_index += 1
        else: # we're inside a tag
            if tagged_string[tagged_index] == '>':
                in_a_tag = False
                outstring += '>'
            else: # we're inside a tag, keep going
                outstring += tagged_string[tagged_index]
        tagged_index += 1
    return outstring

def change_case(input_string):
    if '<' in input_string:  # does it have at least the start of one tag?
        return process_tagged_string(input_string) # treat it specially
    return call_SE_titlecase(input_string)  # no tags, so just the quick and simple way

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Titlecase a string correctly even if it includes tags.')

    # Add the string parameter
    parser.add_argument('input_string', type=str, help='The input string to titlecase.')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Change the case of the input string
    altered_string = change_case(args.input_string)

    # Print the altered string
    print(f'Input: {args.input_string}\nOutput: {altered_string}')

if __name__ == '__main__':
    main()