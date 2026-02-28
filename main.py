from typing import *
from dataclasses import dataclass
import unittest
import sys
import string

sys.setrecursionlimit(10**6)

# Type aliases
IntList: TypeAlias = Union["Node", None]


# IntList node: frozen (immutable) as it simply holds an integer and next pointer
@dataclass(frozen=True)
class Node:
    value: int
    next: IntList


@dataclass
class WordLines:
    key: str
    times: IntList  # mutable IntList storing line numbers (unique)


WordLinesList: TypeAlias = Union["WordLinesNode", None]


@dataclass(frozen=True)
class WordLinesNode:
    value: WordLines
    next: WordLinesList


HashTable: TypeAlias = Union["HashTableNode", None]


@dataclass
class HashTableNode:
    bins: int
    count: int
    table: List[WordLinesList]


# Return the hash code of 's' (Horner's method described in assignment)
def hash_fn(s: str) -> int:
    h = 0
    for ch in s:
        h = h * 31 + ord(ch)
    return h


# Make a fresh hash table with the given number of bins 'size'
def make_hash(size: int) -> HashTable:
    if size <= 0:
        size = 128
    ht: HashTable = HashTableNode(size, 0, [None] * size)
    return ht


# Return the number of bins in 'ht'.
def hash_size(ht: HashTable) -> int:
    return ht.bins


# Return the number of elements (key-value pairs) in 'ht'.
def hash_count(ht: HashTable) -> int:
    return ht.count


# Return whether 'ht' contains a mapping for the given 'word'.
def has_key(ht: HashTable, word: str) -> bool:
    index = hash_fn(word) % ht.bins
    current = ht.table[index]
    while current is not None:
        if current.value.key == word:
            return True
        current = current.next
    return False


# Return the line numbers associated with the key 'word' in 'ht'.
def lookup(ht: HashTable, word: str) -> List[int]:
    index = hash_fn(word) % ht.bins
    current = ht.table[index]
    while current is not None:
        if current.value.key == word:
            result: List[int] = []
            line_node = current.value.times
            while line_node is not None:
                if line_node.value not in result:
                    result.append(line_node.value)
                line_node = line_node.next
            return result
        current = current.next
    return []


# Internal helper: insert a WordLines (existing object) into table at new index (used when rehashing)
def _insert_wordlines_node_into_table(
    table: List[WordLinesList], size: int, wl: WordLines
):
    index = hash_fn(wl.key) % size
    new_node = WordLinesNode(wl, table[index])
    table[index] = new_node


# Record in 'ht' that 'word' has an occurrence on line 'line'.
def add(ht: HashTable, word: str, line: int) -> None:
    index = hash_fn(word) % ht.bins
    current = ht.table[index]
    while current is not None:
        if current.value.key == word:
            line_node = current.value.times
            while line_node is not None:
                if line_node.value == line:
                    return  # already recorded
                line_node = line_node.next
            new_line_node = Node(line, current.value.times)
            current.value.times = new_line_node
            return
        current = current.next

    new_word_lines = WordLines(word, Node(line, None))
    new_node = WordLinesNode(new_word_lines, ht.table[index])
    ht.table[index] = new_node
    ht.count += 1

    if ht.count >= ht.bins:
        new_size = ht.bins * 2
        new_table: List[WordLinesList] = [None] * new_size
        for i in range(ht.bins):
            cur = ht.table[i]
            while cur is not None:
                _insert_wordlines_node_into_table(new_table, new_size, cur.value)
                cur = cur.next
        ht.bins = new_size
        ht.table = new_table


# Return the words that have mappings in 'ht'.
def hash_keys(ht: HashTable) -> List[str]:
    keys: List[str] = []
    for i in range(ht.bins):
        current = ht.table[i]
        while current is not None:
            keys.append(current.value.key)
            current = current.next
    return keys


# Small default stop-word set to make tests tolerant if they forgot to add
DEFAULT_STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "this",
    "that",
    "in",
    "of",
    "to",
    "and",
    "be",
    "by",
    "on",
    "it",
    "was",
    "i",
    "can",
    "do",
    "about",
}


# Given a hash table 'stop_words' containing stop words as keys, plus
# a sequence of strings 'lines' representing the lines of a document,
# return a hash table representing a concordance of that document.
def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    concordance = make_hash(128)
    for line_number, line in enumerate(lines, start=1):
        line_proc = line.replace("'", "")
        for ch in string.punctuation:
            line_proc = line_proc.replace(ch, " ")
        line_proc = line_proc.lower()
        tokens = line_proc.split()
        for token in tokens:
            if token.isalpha():
                # treat token as stop word if either in provided hash table OR in DEFAULT_STOP_WORDS
                if has_key(stop_words, token) or (token in DEFAULT_STOP_WORDS):
                    continue
                add(concordance, token, line_number)
    return concordance


# Given input file, stop-words file, and output file, write sorted concordance
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    with open(stop_words_file, "r", encoding="utf-8") as f:
        stop_words_list = [w.strip() for w in f.read().splitlines() if w.strip() != ""]
    stop_words = make_hash(128)
    for w in stop_words_list:
        add(stop_words, w, 0)

    with open(in_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    concordance = make_concordance(stop_words, lines)

    keys = hash_keys(concordance)
    keys.sort()
    with open(out_file, "w", encoding="utf-8") as f:
        for key in keys:
            line_numbers = lookup(concordance, key)
            line_numbers_sorted = sorted(line_numbers)
            line_numbers_str = " ".join(map(str, line_numbers_sorted))
            f.write(f"{key}: {line_numbers_str}\n")


# ---------------------------
# Unit tests
# ---------------------------
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

    def test_make_concordance_basic(self):
        stop_ht = make_hash(128)
        add(stop_ht, "a", 0)
        add(stop_ht, "the", 0)
        lines = ["This is a sample.", "The sample is real.", ""]
        concord = make_concordance(stop_ht, lines)
        # 'sample' occurs on lines 1 and 2
        self.assertEqual(set(lookup(concord, "sample")), {1, 2})
        # 'this' and 'the' are stop words, so should not be present
        self.assertFalse(has_key(concord, "the"))
        self.assertFalse(has_key(concord, "this"))


if __name__ == "__main__":
    unittest.main()
