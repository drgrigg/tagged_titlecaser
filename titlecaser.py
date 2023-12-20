#! /usr/bin/env python3

from pathlib import Path
import subprocess
import regex
import argparse


def call_SE_titlecase(uncased: str) -> str:
    command = f'se titlecase "{uncased}"'
    output = subprocess.check_output(command, shell=True, encoding="utf-8")
    return output.strip()


def check_badly_formed(tagged_string) -> bool:
    # we know from earlier in the call stack that there's at least one < char
    # but we need to know if the start of the string is already INSIDE a tag
    right_angle_index = tagged_string.find(">")
    left_angle_index = tagged_string.find("<")
    return (
        right_angle_index < left_angle_index
    )  # True if the first right angle is BEFORE the first left angle


def remove_tags(tagged_string: str) -> str:
    # take out the tags by transcribing and omitting them
    # with a well-formed string we could do this more efficiently with a regex,
    # but this way is more certain in case a string is badly formed, eg 'h3>A TITLE</h3'
    untagged = ""
    in_a_tag = check_badly_formed(tagged_string)
    tagged_index = 0
    while tagged_index < len(tagged_string):
        if not in_a_tag:
            if tagged_string[tagged_index] == "<":
                in_a_tag = True
            else:
                untagged += tagged_string[tagged_index]  # transfer the char
        else:  # we're inside a tag
            if tagged_string[tagged_index] == ">":
                in_a_tag = False
        tagged_index += 1
    return untagged.strip()


def process_tagged_string(tagged_string: str):
    untagged = remove_tags(tagged_string)
    cased = call_SE_titlecase(uncased=untagged)
    tagged_index = 0
    untagged_index = 0
    in_a_tag = check_badly_formed(tagged_string)
    outstring = ""
    while tagged_index < len(tagged_string):
        if not in_a_tag:
            if tagged_string[tagged_index] == "<":
                in_a_tag = True
                outstring += "<"
            else:
                outstring += cased[untagged_index]  # transfer the titlecased letter
                untagged_index += 1
        else:  # we're inside a tag
            if tagged_string[tagged_index] == ">":
                in_a_tag = False
                outstring += ">"
            else:  # we're inside a tag, keep going
                outstring += tagged_string[tagged_index]
        tagged_index += 1
    return outstring


# we compile these once here for efficiency
semantic_pattern = regex.compile(r'<i epub:type="se:name\.(.*?)"(.*?)>(.*?)</i>')
heading_pattern = regex.compile(r"<h(\d)(.*?)>(.*?)</h\1>")
title_pattern = regex.compile(r'epub:type="(title|subtitle)">(.*?)<')


def change_case(input_string: str):
    if "<" not in input_string:  # if no tags, process normally
        return call_SE_titlecase(uncased=input_string)
    else:
        cased_string = process_tagged_string(input_string)  # treat it specially
        # now we have to check for book, play, etc titles and process them again as separate units
        for match in semantic_pattern.finditer(
            cased_string
        ):  # we iterate because there may be more than one such
            # we make a recursive call because the book title may contain tags of its own such as <abbr>
            titled_semantic = change_case(match.group(3), regex.IGNORECASE)
            replacement = f'<i epub:type="se:name.{match.group(1)}"{match.group(2)}>{titled_semantic}</i>'
            cased_string = cased_string.replace(match.group(0), replacement)
        return cased_string


def process_file(file_path: str):
    print(f"processing {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    newlines = []
    for line in lines:
        # first search for epub:type of title or subtitle
        match = title_pattern.search(line, regex.IGNORECASE)
        if match:
            source_str = match.group(0)
            uncased = match.group(2)
            cased = change_case(uncased)
            replace_str = f'epub:type="{match.group(1)}">{cased}<'
            newlines.append(line.replace(source_str, replace_str))
        else: # didn't find an epub:type, so just look for h2, h3, etc tags
            match = heading_pattern.search(line, regex.IGNORECASE)
            if match:
                if "roman" in match.group(2) or "ROMAN" in match.group(2):
                    newlines.append(line)
                    continue  # skip it
                source_str = match.group(0)
                uncased = match.group(3)
                cased = change_case(uncased)
                replace_str = (
                    f"<h{match.group(1)}{match.group(2)}>{cased}</h<{match.group(1)}>"
                )
                newlines.append(line.replace(source_str, replace_str))
            else: # didn't find either type, so just pass on the line
                newlines.append(line)
    with open(file_path, "w", encoding="utf-8") as outfile:
        for line in newlines:
            outfile.write(line)


def main():
    parser = argparse.ArgumentParser(
        description="Helper app to titlecase titles and headings in an SE project"
    )
    parser.add_argument(
        "directory", metavar="DIRECTORY", help="a Standard Ebooks source directory"
    )
    args = parser.parse_args()
    folder = Path(args.directory)

    exclude_list = [
        "colophon.xhtml",
        "imprint.xhtml",
        "uncopyright.xhtml",
        "titlepage.xhtml",
        "toc.xhtml",
    ]

    # Iterate over all files in the folder and its subfolders
    for file_path in folder.glob("**/*" + ".xhtml"):
        # Process the file here
        if file_path.name not in exclude_list:
            process_file(file_path)


if __name__ == "__main__":
    main()
