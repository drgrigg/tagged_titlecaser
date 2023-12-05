#! /usr/bin/env python3

import argparse
import subprocess
import regex

def call_SE_titlecase(uncased: str) -> str:
    command = f'se titlecase "{uncased}"'
    output = subprocess.check_output(command, shell=True, encoding='utf-8')
    return output.strip()


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
    return untagged.strip()


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


def change_case(input_string: str, case: str, regex_pattern):
    if '<' in input_string:  # does it have at least the start of one tag?
        cased_string = process_tagged_string(input_string, case) # treat it specially
        if case == 'titlecase':
            # now we have to check for book, play, etc titles and process them again as separate units
            for match in regex_pattern.finditer(cased_string):  # we iterate because there may be more than one such
                # we make a recursive call because the book title may contain tags of its own such as <abbr>
                titled_semantic = change_case(match.group(3), case, regex_pattern) 
                replacement = f'<i epub:type="se:name.{match.group(1)}"{match.group(2)}>{titled_semantic}</i>'
                cased_string = cased_string.replace(match.group(0), replacement)
        return cased_string
    else:
        return do_case_change(uncased=input_string, case=case)


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Change case of a string correctly even if it includes tags.')

    parser.add_argument('--input', help='input file with test cases', required=True)

    parser.add_argument('--output', help='output file to accept processed test cases', required=True)

    # option for kind of casing we want to do
    parser.add_argument('--case', choices=['lower', 'upper', 'titlecase'], default='titlecase', help='Desired case (default: titlecase)')

    # Parse the command-line arguments
    args = parser.parse_args()
    case_wanted = args.case

    # we compile this once here for efficiency
    semantic_pattern = regex.compile(r'<i epub:type="se:name\.(.*?)"(.*?)>(.*?)</i>')

    with open(args.input, 'r') as infile:
        lines = infile.readlines()
        with open(args.output, 'w') as outfile:
            for line in lines:
                changed = change_case(line.strip(), case_wanted, semantic_pattern)
                outfile.write(changed + '\n')

    # Change the case of the input string
    # altered_string = change_case(args.input_string, case_wanted)


if __name__ == '__main__':
    main()