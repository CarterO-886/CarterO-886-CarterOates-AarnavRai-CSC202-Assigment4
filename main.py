from typing import *
from dataclasses import dataclass
import unittest
import sys
import string

sys.setrecursionlimit(10**6)

# =========================
# Data Definitions
# =========================


@dataclass(frozen=True)
class Node:
    value: int
    next: "IntList"


IntList: TypeAlias = Optional[Node]


@dataclass
class WordLines:
    key: str
    times: IntList


@dataclass(frozen=True)
class WordLinesNode:
    value: WordLines
    next: "WordLinesList"


WordLinesList: TypeAlias = Optional[WordLinesNode]


@dataclass
class HashTableNode:
    bins: int
    count: int
    table: List[WordLinesList]


HashTable: TypeAlias = Optional[HashTableNode]


# =========================
# Hash Function
# =========================


def hash_fn(s: str) -> int:
    h = 0
    for ch in s:
        h = h * 31 + ord(ch)
    return h


# =========================
# Hash Table Functions
# =========================


def make_hash(size: int) -> HashTable:
    if size <= 0:
        size = 128
    return HashTableNode(size, 0, [None] * size)


def hash_size(ht: HashTable) -> int:
    return ht.bins


def hash_count(ht: HashTable) -> int:
    return ht.count


def has_key(ht: HashTable, word: str) -> bool:
    index = hash_fn(word) % ht.bins
    current = ht.table[index]
    while current is not None:
        if current.value.key == word:
            return True
        current = current.next
    return False


def lookup(ht: HashTable, word: str) -> List[int]:
    index = hash_fn(word) % ht.bins
    current = ht.table[index]
    while current is not None:
        if current.value.key == word:
            result: List[int] = []
            line_node = current.value.times
            while line_node is not None:
                result.append(line_node.value)
                line_node = line_node.next
            return result
        current = current.next
    return []


def _rehash(ht: HashTable) -> None:
    new_size = ht.bins * 2
    new_table: List[WordLinesList] = [None] * new_size

    for i in range(ht.bins):
        current = ht.table[i]
        while current is not None:
            wl = current.value
            new_index = hash_fn(wl.key) % new_size
            new_node = WordLinesNode(wl, new_table[new_index])
            new_table[new_index] = new_node
            current = current.next

    ht.bins = new_size
    ht.table = new_table


def add(ht: HashTable, word: str, line: int) -> None:
    index = hash_fn(word) % ht.bins
    current = ht.table[index]

    # Word already exists
    while current is not None:
        if current.value.key == word:
            line_node = current.value.times
            while line_node is not None:
                if line_node.value == line:
                    return
                line_node = line_node.next
            current.value.times = Node(line, current.value.times)
            return
        current = current.next

    # Word not found — insert new
    new_word = WordLines(word, Node(line, None))
    new_node = WordLinesNode(new_word, ht.table[index])
    ht.table[index] = new_node
    ht.count += 1

    if ht.count >= ht.bins:
        _rehash(ht)


def hash_keys(ht: HashTable) -> List[str]:
    keys: List[str] = []
    for i in range(ht.bins):
        current = ht.table[i]
        while current is not None:
            keys.append(current.value.key)
            current = current.next
    return keys


# =========================
# Concordance Functions
# =========================


def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    concordance = make_hash(128)

    for line_number, line in enumerate(lines, start=1):
        line = line.replace("'", "")
        for ch in string.punctuation:
            line = line.replace(ch, " ")
        line = line.lower()
        tokens = line.split()

        for token in tokens:
            if token.isalpha() and not has_key(stop_words, token):
                add(concordance, token, line_number)

    return concordance


def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    with open(stop_words_file, "r", encoding="utf-8") as f:
        stop_words_list = f.read().splitlines()

    stop_words = make_hash(128)
    for word in stop_words_list:
        add(stop_words, word.strip().lower(), 0)

    with open(in_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    concordance = make_concordance(stop_words, lines)

    keys = hash_keys(concordance)
    keys.sort()

    with open(out_file, "w", encoding="utf-8") as f:
        for key in keys:
            line_numbers = sorted(lookup(concordance, key))
            numbers_str = " ".join(map(str, line_numbers))
            f.write(f"{key}: {numbers_str}\n")


# =========================
# Unit Tests
# =========================


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

    def test_make_concordance(self):
        stop_ht = make_hash(128)
        add(stop_ht, "a", 0)
        add(stop_ht, "the", 0)
        add(stop_ht, "this", 0)

        lines = ["This is a sample.", "The sample is real.", ""]

        concord = make_concordance(stop_ht, lines)

        self.assertEqual(set(lookup(concord, "sample")), {1, 2})
        self.assertFalse(has_key(concord, "this"))
        self.assertFalse(has_key(concord, "the"))


if __name__ == "__main__":
    unittest.main()
