#!/bin/bash

mkdir -p data
cd data
wget -q https://data.statmt.org/ContraWSD/wsd_testset_corpora_de_en.tar.bz2
tar xjvf wsd_testset_corpora_de_en.tar.bz2

# wget -q https://data.statmt.org/ContraWSD/nc11_de_fr_sentence_aligned.tar.bz2
# wget -q https://data.statmt.org/ContraWSD/wsd_testset_corpora_de_fr.tar.bz2
