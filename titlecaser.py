#! /usr/bin/env python3

import argparse
import regex

def call_SE_titlecase(astring) -> str:
    # this is of course just a dummy, we'd call the real SE titlecase function here
    return astring.title()

def process_tagged_string(tagged_string):
    untagged = regex.sub(r'<.*?>', '', tagged_string)
    titled = call_SE_titlecase(untagged)
    tagged_index = 0
    untagged_index = 0
    in_a_tag = False
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
        # print(outstring)
    return outstring

def change_case(input_string):
    if regex.search(r"<.*?>", input_string):  # does it have at least one tag?
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