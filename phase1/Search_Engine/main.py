import os
import re
import ast


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


try:
    f = open("Inverted_index/inverted.txt")
    # Do something with the file
except IOError:
    print("please wait till generated")
    generate_inverted_index('docs', get_files_directories('docs'))
    f = open("Inverted_index/inverted.txt")
inverted_index = ast.literal_eval(f.read())
query = input('please enter a query:').split()
query = {'query': query}
queries = normalize(query)['query']

if len(queries) == 1:
    try:
        docs = inverted_index[queries[0]]
        for doc in docs:
            print(doc[0])
    except:
        print('no result')
else:
    res = {}
    for query in queries:
        try:
            res[query] = inverted_index[query]
        except:
            continue
    final_res = {}
    for query in queries:
        try:
            for result in res[query]:
                if result[0] not in final_res.keys():
                    final_res[result[0]] = 1
                else:
                    final_res[result[0]] += 1
        except:
            continue
    sorted_keys = sorted(final_res, key=final_res.get, reverse=True)
    for key in sorted_keys:
        print(key)
