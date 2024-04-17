"""
The idea of this script is to essentially release you from the worry of
having to manually add 
"""
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.getcwd())
load_dotenv()
from src.utils.fileops import read_files, write_files

import re
from typing import Set



VAULT = os.environ["VAULT"]


def find_wikilinks(text: str) -> Set[str]:
    """
    Extracts all unique "wikilinks" (links in the format [[link]]) from the given text.

    Args:
        text (str): The text from which to extract wikilinks.

    Returns:
        Set[str]: A set of unique wikilinks found in the text, without the double brackets.

    Example:
        Input: 'Example of a wikilink [[Main Page]], and another [[Python (programming language)|Python]].'
        Output: {'Main Page', 'Python (programming language)|Python'}
    """
    pattern = r"\[\[(.*?)\]\]"
    matches = re.findall(pattern, text)
    return set(matches)

def wikilink_unmarked(text, wikilink_set):
    # Build a regex that matches any word in the wikilink set as a whole word, considering pre-existing wikilinks
    words_regex = r'\b(' + '|'.join(map(re.escape, wikilink_set)) + r')\b(?!\]\])'

    # Function to replace each match with a wikilinked version if it's not already wikilinked
    def replace_unlinked(match):
        word = match.group(0)
        # Build the wikilinked form of the word
        wikilinked_word = f'[[{word}]]'
        # Get the match start and end positions
        start, end = match.span()
        # Check if the match is already wikilinked
        if start >= 2 and text[start-2:start] == '[[' and end + 2 <= len(text) and text[end:end+2] == ']]':
            return word  # return as is if already wikilinked
        return wikilinked_word  # return wikilinked word

    # Substitute occurrences of the words with the replace function
    modified_text = re.sub(words_regex, replace_unlinked, text)

    return modified_text

if __name__ == "__main__":
    # Read all files in the vault
    files = read_files(VAULT)
    for filename in files:
        file_content = files[filename]
        wikilink_set = find_wikilinks(file_content)
        modified_text = wikilink_unmarked(file_content, wikilink_set)
        files[filename] = modified_text
    # Write the modified files back to the vault
    write_files(files, VAULT)