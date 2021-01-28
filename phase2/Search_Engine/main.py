import os
import re
import ast
import math


class MaxHeap:
    def __init__(self):

        self.heap_list = [[0, 0]]
        self.current_size = 0

    def sift_up(self, i):
        while i // 2 > 0:
            if self.heap_list[i][1] > self.heap_list[i // 2][1]:
                self.heap_list[i], self.heap_list[i // 2] = self.heap_list[i // 2], self.heap_list[i]
            i = i // 2

    def insert(self, k):
        self.heap_list.append(k)
        self.current_size += 1
        self.sift_up(self.current_size)

    def sift_down(self, i):
        while (i * 2) <= self.current_size:
            mc = self.max_child(i)
            if self.heap_list[i][1] < self.heap_list[mc][1]:
                self.heap_list[i], self.heap_list[mc] = self.heap_list[mc], self.heap_list[i]
            i = mc

    def max_child(self, i):
        if (i * 2) + 1 > self.current_size:
            return i * 2
        else:
            if self.heap_list[i * 2] > self.heap_list[(i * 2) + 1]:
                return i * 2
            else:
                return (i * 2) + 1

    def delete_max(self):
        if len(self.heap_list) == 1:
            return 'Empty heap'

        root = self.heap_list[1]

        self.heap_list[1] = self.heap_list[self.current_size]

        *self.heap_list, _ = self.heap_list

        self.current_size -= 1

        self.sift_down(1)

        return root


def import_stop_words():
    f = open('resources/stopwords.txt', 'r')
    stopwords = f.read().split('\n')
    return stopwords


def import_jam_words():
    f = open('resources/jam_ha.txt', 'r')
    stopwords = f.read().split('\n')
    return stopwords


def get_files_directories(directory):
    files = os.listdir(directory)
    return files


def generate_inverted_index(dir, files):
    arr = {}
    file_map = {}
    i = 0
    for file in files:
        file_map[i] = file
        f = open(dir + '/' + file, 'r')
        arr[i] = f.read().split()
        i += 1
    normal = normalize(arr)
    inverted_index = {}
    for key in normal:
        for token in normal[key]:
            if token not in inverted_index:
                inverted_index[token] = []
                for key1 in normal:
                    count = 0
                    for token1 in normal[key1]:
                        if token == token1:
                            count += 1
                    if count != 0:
                        inverted_index[token].append((file_map[key1], count))
            else:
                continue
    f = open("Inverted_index/inverted.txt", "w")
    f.write(str(inverted_index))


def normalize(arr_tokens):
    normal_out = {}
    stopwords = import_stop_words()
    for key in arr_tokens:
        for token in arr_tokens[key]:
            # delete stopwords
            if token not in stopwords:
                # check if token is number delete them
                if re.match(r'^-?\d+(?:\.\d+)?$', token) is not None:
                    continue
                elif token.find('.') != -1 or token.find('/') != -1 or token.find('؟') != -1 or token.find(
                        '?') != -1 or token.find('!') != -1 or token.find(':') != -1:
                    token = token.replace('.', '')
                    token = token.replace('?', '')
                    token = token.replace('؟', '')
                    token = token.replace(':', '')
                    token = token.replace('!', '')
                    token = token.replace('/', '')
                    # here we find verbs
                    if token not in stopwords:
                        # delete می in begin of verb
                        if token.startswith('می'):
                            token = token[3:len(token)]
                        if token.startswith('نمی'):
                            token = token[4:len(token)]
                        if token.endswith('یم'):
                            token = token[0:-2]
                        if token.endswith('م'):
                            token = token[0:-1]
                        if token.endswith('ند'):
                            token = token[0:-2]
                        if token.endswith('ید'):
                            token = token[0:-2]
                        if key not in normal_out.keys():
                            normal_out[key] = []
                        normal_out[key].append(token)

                    else:
                        continue
                # here are nouns
                else:
                    token = token.replace('،', '')
                    token = token.replace('\u200c', '')
                    token = token.replace('؛', '')
                    token = token.replace(')', '')
                    token = token.replace('(', '')
                    jam = import_jam_words()
                    if token not in jam:
                        if token.endswith('ان'):
                            token = token[0:-2]
                        elif token.endswith('جات'):
                            token = token[0:-3]
                        elif token.endswith('ها'):
                            token = token[0:-2]
                        elif token.endswith('گان'):
                            token = token[0:-3]
                    if token.endswith('تر'):
                        token = token[0:-2]
                    elif token.endswith('ترین'):
                        token = token[0:-4]
                    elif token.endswith('ست'):
                        token = token[0:-2]
                    if key not in normal_out.keys():
                        normal_out[key] = []
                    normal_out[key].append(token)
            else:
                continue
    return normal_out


def generate_td_idf(inverted_indexes, dictionary):
    td_idfs = {}
    for key1 in inverted_indexes:
        for file in inverted_indexes[key1]:
            if file not in td_idfs.keys():
                td_idfs[file[0]] = []
    n = len(td_idfs)
    idfs = {}
    for word in dictionary:
        inverted_index = inverted_indexes[word]
        n_temp = len(inverted_index)
        idfs[word] = math.log(n / n_temp)
    for key in td_idfs:
        for word in dictionary:
            inverted_index = inverted_indexes[word]
            files = {}
            for file in inverted_index:
                files[file[0]] = file[1]
            if key in files:
                td_idfs[key].append((1 + math.log(files[key] + 1)) * idfs[word])
            else:
                td_idfs[key].append((1 + math.log(1)) * idfs[word])
    for key in td_idfs:
        size = 0
        for item in td_idfs[key]:
            size += item ** 2
        size = size ** 0.5
        td_idfs[key] = [x / size for x in td_idfs[key]]
    f = open("td_idf/td_idfs.txt", "w")
    f.write(str(td_idfs))
    f.close()


def query_tf_idf(query, dictionary, inverted_indexes):
    td_idf = []
    idfs = {}
    n = len(dictionary)
    for word in dictionary:
        inverted_index = inverted_indexes[word]
        n_temp = len(inverted_index)
        idfs[word] = math.log(n / n_temp)
    for word in dictionary:
        if word in query:
            td_idf.append((1 + math.log(2)) * idfs[word])
        else:
            td_idf.append(0)
    return td_idf


def cosine_similarity(tf_idfs, query_idf):
    output = {}
    for key in tf_idfs:
        score = 0
        i = 0
        for x in tf_idfs[key]:
            score += x * query_idf[i]
            i += 1
        output[key] = score
    return output


def generate_champions_list(inverted_index):
    champion_list = {}
    for key in inverted_index:
        for item in inverted_index[key]:
            if key not in champion_list:
                champion_list[key] = []
            if item[1] >= 1:
                champion_list[key] = (item[0], item[1])
    f = open("champion_list/champion_list.txt", "w")
    f.write(str(champion_list))
    f.close()


try:
    f = open('Inverted_index/inverted.txt')
    inverted_index = ast.literal_eval(f.read())
    f.close()
    dictionary = list(inverted_index.keys())
    f = open("td_idf/td_idfs.txt")
    tf_idfs = ast.literal_eval(f.read())
    f = open('champion_list/champion_list.txt')
    champion_list = ast.literal_eval(f.read())
except IOError:
    print("please wait till generated")
    generate_inverted_index('docs', get_files_directories('docs'))
    f = open('Inverted_index/inverted.txt')
    inverted_index = ast.literal_eval(f.read())
    dictionary = list(inverted_index.keys())
    generate_td_idf(inverted_index, dictionary)
    f = open("td_idf/td_idfs.txt")
    tf_idfs = ast.literal_eval(f.read())
    generate_champions_list(inverted_index)
    f = open('champion_list/champion_list.txt')
    champion_list = ast.literal_eval(f.read())

query = input('please enter a query:').split()
query = {'query': query}
queries = normalize(query)['query']
tf_idf_query = query_tf_idf(queries, dictionary, inverted_index)
file_in_ch_list = []
for x in queries:
    if x in champion_list:
        files = champion_list[x]
        for file in files:
            file_in_ch_list.append(file)
output = cosine_similarity(tf_idfs, tf_idf_query)
max_heap = MaxHeap()
for x in output:
    max_heap.insert([x, output[x]])

k =10
for i in range(k):
    print(max_heap.delete_max())
