#!/usr/bin/env python3

from __future__ import unicode_literals

import os
import sys
import json
import argparse

from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ContraPro", "bin"))
from json2text import build_doc, read_dir_recursive

BASEDIR = Path(__file__).parent


parser = argparse.ArgumentParser()
parser.add_argument("json_file", default="de-en.final.json")
parser.add_argument("--source-lang", default="de")
parser.add_argument("--target-lang", default="en")
parser.add_argument("--output", type=argparse.FileType("w"), default=sys.stdout)
parser.add_argument("--dir", "-d", default=BASEDIR / "data" / "wsd_testset_corpora_de_en")
parser.add_argument("--max-sents", "-ms", type=int, default=0, help="Maximum number of context sentences")
parser.add_argument("--max-tokens", "-m", type=int, default=250, help="Maximum length in subword tokens (default: %(default)s)")
parser.add_argument("--sents-before", "-sb", type=int, default=None, help="Num sentences previous context")
parser.add_argument("--tokens-before", "-tb", type=int, default=None, help="Num tokens in previous context")
parser.add_argument("--separator", default=" <eos> ")
parser.add_argument("--spm")
args = parser.parse_args()


spm = None
if args.spm:
    from sentencepiece import SentencePieceProcessor
    spm = SentencePieceProcessor(model_file=args.spm)


documents = read_dir_recursive(args.dir, args.source_lang, args.target_lang)
jsondata = json.load(open(args.json_file))

for sentence in jsondata:
    filename = sentence["origin"]
    if not filename in documents:
        print("Fatal: missing file: {filename}", file=sys.stderr)

    lineno = int(sentence["sentence number"]) - 1

    source = sentence["source"]
    reference = sentence["reference"]

    def count_tokens(line):
        if type(line) == str:
            line = [line]

        if spm:
            return len(spm.encode(args.separator.join(line)))
            # print(length, spm.encode(args.separator.join(context + [source])))
        else:
            return len(args.separator.join(line).split())
            # print(length, args.separator.join(context + [source]).split())

    def is_too_long(source_doc):
        """Return True if the context + source sentence is too long."""
        length = count_tokens(source_doc)
        return (args.max_tokens > 0 and length > args.max_tokens) or (args.max_sents > 0 and len(source_doc) - 1 > args.max_sents)

    source_lines, target_lines, target_index = build_doc(is_too_long, count_tokens, lineno, documents[filename], num_before=args.sents_before, tokens_before=args.tokens_before)

    source_line = args.separator.join(source_lines)
    target_line = args.separator.join(target_lines)

    print(target_index, "correct", sentence["original translation"], source_line, target_line, sep="\t")
    for error in sentence['errors']:
        target_lines[target_index] = error["contrastive"]
        target_line = args.separator.join(target_lines)
        print(target_index, "contrastive", error["replacement"], source_line, target_line, sep="\t")

