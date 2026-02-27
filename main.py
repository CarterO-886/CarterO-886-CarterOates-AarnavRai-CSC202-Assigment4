from typing import *
from dataclasses import dataclass
import unittest
import sys
import string
sys.setrecursionlimit(10**6)


IntList : TypeAlias = Union['Node',None]
@dataclass
class Node:
    value: int
    next: IntList

@dataclass
class WordLines:
    key: str
    times: IntList

WordLinesList : TypeAlias = Union['WordLinesNode',None]
@dataclass
class WordLinesNode:
    value: WordLines
    next: WordLinesList

HashTable : TypeAlias = Union['HashTableNode',None]
@dataclass
class HashTableNode:
    bins: int
    count: int
    table: List[WordLinesList]

# Make a fresh hash table with the given number of bins 'size', 128
# containing no elements.
def make_hash(size: int) -> HashTable:
    size = 128
    ht : HashTable = HashTableNode(size, 0, [None] * size) # create hashtable with set number of bins
    return ht

# Return the hash code of 's' (see assignment description).
def hash_fn(s: str) -> int:
    hash_code = 0  # resetting hash code for new charcter
    for char in s:
        hash_code = (hash_code * 31 + ord(char)) % (2**32) # hash code from assignment
    return hash_code

# Return the number of bins in 'ht'.
def hash_size(ht: HashTable) -> int:
    return ht.bins # bins is an int contained in HashTable data structure

# Return the number of elements (key-value pairs) in 'ht'.
def hash_count(ht: HashTable) -> int:
    return ht.count # number of elements is contained as an int in HastTable data structure

    
# Return whether 'ht' contains a mapping for the given 'word'.
def has_key(ht: HashTable, word: str) -> bool:
    index = hash_fn(word) % ht.bins # acquiring the hashcode and the bin assignent of the word
    current = ht.table[index] # finding key value pair
    while current is not None: 
        if current.value.key == word: #found
            return True
        current = current.next # not found
    return False # not found at all

# Return the line numbers associated with the key 'word' in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def lookup(ht: HashTable, word: str) -> List[int]:
    index = hash_fn(word) % ht.bins # finding the bin assignmet of the word
    current = ht.table[index] # finding bin, now it is an index of List[WordList]
    while current is not None: 
        if current.value.key == word: 
            lines = []
            line_node = current.value.times
            while line_node is not None:
                if line_node.value not in lines:
                    lines.append(line_node.value)
                line_node = line_node.next
            return lines
        current = current.next
    return []




# Record in 'ht' that 'word' has an occurrence on line 'line'.
def add(ht: HashTable, word: str, line: int) -> None:
    index = hash_fn(word) % ht.bins
    current = ht.table[index]
    while current is not None:
        if current.value.key == word: # if word is already in list
            # Add line to the existing WordLines
            line_node = current.value.times
            while line_node is not None:
                if line_node.value == line:
                    return  # Line already recorded, do nothing
                line_node = line_node.next
            # Add new line to the front of the times list
            new_line_node = Node(line, current.value.times) # adding to linked list of lines that word occurs on
            current.value.times = new_line_node 
            return
        current = current.next #go on, word is not in the list
    
    # Word not found, create a new WordLines and add it to the hash table
    new_word_lines = WordLines(word, Node(line, None)) # add new key to wordline/adding index to list
    
    new_word_lines_node = WordLinesNode(new_word_lines, ht.table[index]) # Add new value at index associated with word's hash
    ht.table[index] = new_word_lines_node
    ht.count += 1
    
    # Check if resizing is needed (load factor >= 1.0)
    if ht.count >= ht.bins:
        # Create a new hash table with double the size
        new_size = ht.bins * 2
        new_table = [None] * new_size
        
        # Rehash all key-value pairs due to new new size of bins
        for i in range(ht.bins):
            current = ht.table[i]
            while current is not None:
                # Rehash to new table
                new_index = hash_fn(current.value.key) % new_size
                new_node = WordLinesNode(current.value, new_table[new_index])
                new_table[new_index] = new_node
                current = current.next
        
        # Update the hash table
        ht.bins = new_size
        ht.table = new_table


# Return the words that have mappings in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def hash_keys(ht: HashTable) -> List[str]:
    keys = []
    for i in range(ht.bins):
        current = ht.table[i]
        while current is not None:
            keys.append(current.value.key) #don't need to check if word is in there twice because prev functions handle that
            current = current.next
    return keys #returning all the different unique words encountered

# Given a hash table 'stop_words' containing stop words as keys, plus
# a sequence of strings 'lines' representing the lines of a document,
# return a hash table representing a concordance of that document.
def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    concordance = make_hash(128)
    for line_number, line in enumerate(lines, start=1):
        # Remove apostrophes
        line = line.replace("'", "")
        # Replace all punctuation with spaces
        for char in string.punctuation:
            line = line.replace(char, " ")
        # Convert to lowercase
        line = line.lower()
        # Split into tokens
        tokens = line.split()
        # Process each token
        for token in tokens:
            # Keep only tokens where isalpha() returns True
            if token.isalpha() and not has_key(stop_words, token):
                add(concordance, token, line_number)
    return concordance

# Given an input file path, a stop-words file path, and an output file path,
# overwrite the indicated output file with a sorted concordance of the input file
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    with open(stop_words_file, 'r') as f:
        stop_words_list = f.read().splitlines()
    
    stop_words = make_hash(128)
    for word in stop_words_list:
        add(stop_words, word, 0)  # Line number is irrelevant for stop words
    
    with open(in_file, 'r') as f:
        lines = f.read().splitlines()
    
    concordance = make_concordance(stop_words, lines)
    
    keys = hash_keys(concordance)
    keys.sort()
    
    with open(out_file, 'w') as f:
        for key in keys:
            line_numbers = lookup(concordance, key)
            line_numbers_str = ', '.join(map(str, sorted(line_numbers)))
            f.write(f"{key}: {line_numbers_str}\n")





class Tests(unittest.TestCase):
        def test_make_hash(self):
            ht = make_hash(128)
            self.assertEqual(hash_size(ht), 128)
            self.assertEqual(hash_count(ht), 0)
    
        def test_add_and_lookup(self):
            ht = make_hash(128)
            add(ht, "hello", 1)
            add(ht, "world", 2)
            add(ht, "hello", 3)
            
            self.assertTrue(has_key(ht, "hello"))
            self.assertTrue(has_key(ht, "world"))
            self.assertFalse(has_key(ht, "test"))
            
            self.assertEqual(set(lookup(ht, "hello")), {1, 3})
            self.assertEqual(set(lookup(ht, "world")), {2})
            self.assertEqual(lookup(ht, "test"), [])
    
        def test_hash_keys(self):
            ht = make_hash(128)
            add(ht, "apple", 1)
            add(ht, "banana", 2)
            add(ht, "cherry", 3)
            
            keys = hash_keys(ht)
            self.assertEqual(set(keys), {"apple", "banana", "cherry"})


if (__name__ == '__main__'):
    unittest.main()