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
        self.block_handles = []

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

    def write_block_to_disk(self, term_postings_list, block_number):
        # Define block
        base_path = 'index_blocks/'
        block_name = 'block-' + str(block_number) + '.txt'
        block = open(base_path + block_name, 'a+')
        print(" -- Writing term-positing list block: " + block_name + "...")
        for index, term in enumerate(term_postings_list):
            block.write(str(term) + ":" + str((term_postings_list[term])) + "\n")
        block.close()
        self.dictionary={}

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
                
                '''Pre-processing'''
                # Tokenizamos nuestro txt
                tokens = nltk.word_tokenize(file_content)
                #Filtramos para que no pertenezca a los stopwords o no sea un valor no alfanumerico (Stopwords / Valores raros)
                terms = [word for word in tokens if not word in TextPreprocessor.stopwords and re.match("^[a-zA-Z]+$", word)]
                #Hacemos Stemming en el idioma respectivo
                terms = [TextPreprocessor.stemmer.stem(w) for w in terms]

                for term in terms:

                    if (sys.getsizeof(term) + sys.getsizeof([docID]) + sys.getsizeof(self.dictionary) > self.block_size_limit):
                        temp_dict = self.sort_terms()
                        self.write_block_to_disk(temp_dict, block_number)
                        temp_dict = {}
                        block_number += 1

                    if term not in self.dictionary:
                        self.dictionary[term] = [docID]
                    else:
                        self.dictionary[term].append(docID)

                if sys.getsizeof(self.dictionary) > self.block_size_limit or (documents_counter == documents_count - 1):
                    temp_dict = self.sort_terms()
                    self.write_block_to_disk(temp_dict, block_number)
                    temp_dict = {}
                    block_number += 1
        print("BLOCKS creation complete!")
        self.merge_blocks()

    #hacer un create del self

    def create(self):
        self.cant_blocks = 0
        self.spimi_invert()

    #Hacer una busuqeda binaria de los bloques para buscar el termino, tienes que halla la similitu de coseno en llo

    def binary_search_term_blocks(self, term, block_handle):
        low = 0
        high = self.cant_blocks - 1
        mid = None
        found = False
        while low <= high and not found:
            mid = int((low + high)/2)
            index = self.binary_search_term[mid]
            key = self.keys[index]
            if key == term:
                return index
            elif key < term:
                low = mid + 1
            else:
                high = mid - 1
        return None
    

    def cosine_similarity(query, total_docs, document_length):
        query_vector = {}
        for term in query:
            if term in total_docs:
                query_vector[term] = 1

        query_length = math.sqrt(sum(query_vector.values()) ** 2)
        scores = []

        for doc_id, postings in total_docs.items():
            doc_length = document_length[doc_id]
            score = 0

            for term, tf_idf in postings.items():
                if term in query_vector:
                    score += query_vector[term] * tf_idf

            score /= (query_length * doc_length)
            heapq.heappush(scores, (-score, doc_id))

        top_scores = []
        while scores:
            top_scores.append(heapq.heappop(scores))

        return top_scores
    
    

    def binary_search_term(self, query):
        result = set()
        words = query.split(' ')
        for word in words:
            postings_list = []
            for block_handle in self.block_handles:
                posting_list_pointer = self.posting_lists[block_handle].get(word)
                if posting_list_pointer is not None:
                    start, end = posting_list_pointer
                    postings_list.extend(range(start, end))
            if len(postings_list) > 0:
                result.add(min(postings_list))
        return sorted(list(result))
            
    def calculate_idf(self, term: str):
        postings_list_term = self.binary_search_term(self.header_terms_file, self.index_file, term)
        if postings_list_term is None:
            return 0
        document_frequency = len(postings_list_term)
        total_documents = self.total_docs
        idf = math.log(float(total_documents) / float(document_frequency), 10)
        return idf
    


        


""""

        
    def calculate_idf(self, term: str):

        tf_idf_dict = {}
        for t, postings in term():
            tf_idf_dict[term] = {}
            df = len(postings)
            idf = math.log(len(self.documents)/df)
            for docId, freq in postings.items():
                tf_idf_dict[term][docId] = (freq * idf)
                return tf_idf_dict

    def lenghts_binary(self, docID):
        doc_vector = self.get_document_vector(docID)
        vector_length = sum(math.sqrt(tf*idf) for tf, idf in doc_vector.items())
        return vector_length
        
    def cosine_similarity(query, total_docs, document_length):
        query_vector = {}
        for term in query:
            if term in total_docs:
                query_vector[term] = 1 
                query_length = math.sqrt(sum(query_vector.values()) ** 2)
                scores = {}
                for term, postings in total_docs.items():
                    for doc_id, tf_idf in postings.items():
                        if doc_id not in scores:
                            scores[doc_id] = 0
                        scores[doc_id] += query_vector.get(term, 0) * tf_idf
                    for doc_id, score in scores.items():
                        scores[doc_id] /= (query_length * document_length[doc_id])
                        return scores

    #idea

    def get_document_vector(self, docID):
        document_vector = [0] * self.total_terms
        postings_list = self.get_postings_list(docID)
        if not postings_list:
            return document_vector
        for term, tf in postings_list:
            term_id = self.get_term_id(term)
            if term_id is not None:
                document_vector[term_id] = tf * self.calculate_idf(term)
        return document_vector

    def get_query_vector(self, query):
        query_vector = [0] * self.total_terms
        query_terms = query.split()
        for term in query_terms:
            term_id = self.get_term_id(term)
            if term_id is not None:
                query_vector[term_id] += 1  
        return query_vector

if __name__ == "__main":
    fashion_processor = FashionDataProcessor('csv/fashion_product_images.csv', 'unprocessed_txt')
    fashion_processor.select_textual_columns()
    fashion_processor.save_to_text_files()

    docID = DEBERIA SER EL CONSINE PARA TODOS LOS DOCS, NO SOLO UNO

    text_preprocessor = TextPreprocessor('unprocessed_txt', 'processed_txt')
    text_preprocessor.process_text_files()

    inverted_index = InvertedIndex('processed_txt', 900 * 100, 'output_folder')
    inverted_index.spimi_invert()
    query = "your query goes here"  # Reemplaza con tu consulta
    cosine_similarity = inverted_index.calculate_cosine_similarity(docID, query)
    print(f"Cosine Similarity between DocID {docID} and Query: {cosine_similarity}")
    """    
    
    