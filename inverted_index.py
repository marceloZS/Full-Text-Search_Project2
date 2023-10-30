import os
import pandas as pd
import numpy as np
import nltk
import re
import sys
import math
import collections
import heapq
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

class FashionDataProcessor:
    def __init__(self, data_file, output_folder):
        self.data = pd.read_csv(data_file, delimiter=',')
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def select_textual_columns(self):
        self.data = self.data[['gender', 'masterCategory', 'subCategory', 'articleType', 'baseColour', 'season', 'year', 'usage', 'productDisplayName']]

    def save_to_text_files(self):
        for index, row in self.data.iterrows():
            row_str = ' '.join(str(item) for item in row)
            file_path = os.path.join(self.output_folder, f'doc{index + 1}.txt')
            with open(file_path, 'w') as file:
                file.write(row_str)

class TextPreprocessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        self.stopwords = stopwords.words('english')
        self.stemmer = SnowballStemmer('english')

    def process_text_files(self):
        for filename in os.listdir(self.input_folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.input_folder, filename)
                file_content = open(filepath, encoding="utf-8").read().lower()
                tokens = nltk.word_tokenize(file_content)
                filtered_text = [word for word in tokens if not word in self.stopwords and re.match("^[a-zA-Z]+$", word)]
                stemmed_text = [self.stemmer.stem(w) for w in filtered_text]
                processed_text = " ".join(stemmed_text)
                output_filepath = os.path.join(self.output_folder, filename)
                with open(output_filepath, 'w', encoding="utf-8") as output_file:
                    output_file.write(processed_text)

class InvertedIndex:
    def __init__(self, input_folder, block_size_limit, output_folder):
        self.input_folder = input_folder
        self.block_size_limit = block_size_limit
        self.output_folder = output_folder
        self.dictionary = {}
        os.makedirs(output_folder, exist_ok=True)

    def sort_terms(self):
        sorted_terms = sorted(self.dictionary)
        sorted_dictionary = {}
        for term in sorted_terms:
            result = [docIds for docIds in self.dictionary[term]]
            result_tftd = self.calculate_tftd(result)
            sorted_dictionary[term] = result_tftd
        return sorted_dictionary

    def calculate_tftd(self, pl_with_duplicates):
        counter = collections.Counter(pl_with_duplicates)
        pl_tftd = [[docId, counter[docId]] for docId in counter.keys()]
        return pl_tftd

    def write_block_to_disk(self, block_number):
        base_path = 'index_blocks/'
        block_name = f'block-{block_number}.txt'
        block = open(os.path.join(base_path, block_name), 'a+')
        for term in self.dictionary:
            block.write(f"{term}:{str(self.dictionary[term])}\n")
        block.close()
        self.dictionary = {}

    def merge_blocks(self):
        block_files = [os.path.join('index_blocks', block) for block in os.listdir('index_blocks')]
        block_files.sort()
        block_handles = [open(file, 'r', encoding='utf-8') for file in block_files]
        merge_heap = []
        term_postings_dict = {}

        for i, block_handle in enumerate(block_handles):
            line = block_handle.readline().strip()
            if line:
                term, postings = line.split(':', 1)
                postings = eval(postings)
                term_postings_dict[term] = postings
                heapq.heappush(merge_heap, (term, i))

        with open(os.path.join(self.output_folder, 'inverted_index.txt'), 'w', encoding='utf-8') as output_handle:
            while merge_heap:
                min_term, block_index = heapq.heappop(merge_heap)
                output_handle.write(f"{min_term}:{str(term_postings_dict[min_term])}\n")
                line = block_handles[block_index].readline().strip()
                if line:
                    term, postings = line.split(':', 1)
                    postings = eval(postings)
                    term_postings_dict[term] = postings
                    heapq.heappush(merge_heap, (term, block_index))
        for block_handle in block_handles:
            block_handle.close()

    def spimi_invert(self):
        documents = os.listdir(self.input_folder)
        documents_count = len(documents)
        documents_counter = 0
        block_number = 0

        for docID in documents:
            if docID.endswith(".txt"):
                documents_counter += 1
                file_route = os.path.join(self.input_folder, docID)
                file_content = open(file_route, encoding="utf-8").read().lower()
                terms = file_content.split()
                for term in terms:
                    if term not in self.dictionary:
                        self.dictionary[term] = [docID]
                    else:
                        self.dictionary[term].append(docID)

                if sys.getsizeof(self.dictionary) > self.block_size_limit or (documents_counter == documents_count - 1):
                    temp_dict = self.sort_terms()
                    self.write_block_to_disk(block_number)
                    block_number += 1
        print("BLOCKS creation complete!")
        self.merge_blocks()

    def _binary_search(self, term):
        sorted_t = sorted(self.dictionary.keys()) 
        left = 0 
        right = len(sorted_t) - 1
        result = []
        
        while left <= right:
            mid = int((left + right) / 2)
            if sorted_t[mid] == term:
                return self.dictionary[sorted_t[mid]]
            elif sorted_t[mid] < term:
                left = mid + 1
            else:
                right = mid - 1
        return None
    
    
    def _search(self, query): 
        result = set([])
        words = query.split(' ')
        for word in words:
            res = self._binary_search(word)
            if res is not None:
                result |= {res}
                return list(result)
            return list(result)
        

        
    def calculate_idf(self, term: str):
        postings_list_term = self._binary_search_term(self.header_terms_file, self.index_file, term)
        if postings_list_term is None:
            return 0
        df_term = len(postings_list_term)
        return math.log10(self.n / (df_term + 1))  

    def calculate_document_normalization(self, docID):
        doc_vector = self.get_document_vector(docID)
        if not doc_vector:
            return 0
        return math.sqrt(sum(w ** 2 for w in doc_vector))   
        
    def calculate_cosine_similarity(self, docID, query):
        query_vector = self.get_query_vector(query)
        if not query_vector:
            return 0
        doc_vector = self.get_document_vector(docID)
        if not doc_vector:
            return 0
        dot_product = sum(q * d for q, d in zip(query_vector, doc_vector))
        query_norm = math.sqrt(sum(q ** 2 for q in query_vector))
        doc_norm = self.calculate_document_normalization(docID)
        if query_norm == 0 or doc_norm == 0:
            return 0
        return dot_product / (query_norm * doc_norm)
