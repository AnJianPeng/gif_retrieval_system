import json
import re
import os.path as osp
from nltk.corpus import stopwords
from stanfordcorenlp import StanfordCoreNLP

import api.tquery.skip_list as sl
import api.tquery.trie as tr

'''
Deal with various queries
'''

'''
Methods to compute intersection of multiple posting lists
The posting lists are saved in SkipList data structure
Get intersection by forwarding pointers of different SkipLists to find common elements
'''
def comp_intersection(skip_lists):
    intr_sect = []
    target = 0 # our target are GIF IDs which are positive
    finish = False
    while not finish:
        current_target = target
        for l in skip_lists:
            target = l.forward(target)
            if  target == -1:
                # we have reached the end of one list without finding valid target
                finish = True
                break
        if finish:
            break
        if target == current_target:
            intr_sect.append(current_target)
            print(current_target)
            target += 1

    return intr_sect


'''
Parse the query passed from front-end
And complete the query
'''
def run(trie, query):
    pattern = re.compile("[a-zA-Z]+(\s+AND\s+[a-zA-Z]+)+$")
    m = pattern.match(query)

    nlp = StanfordCoreNLP('http://localhost', port=9000, timeout=30000)
    props = {'annotators': 'pos,lemma',
             'pipelineLanguage': 'en',
             'outputFormat': 'json'}
    query = re.sub("[\+\.\!\/_,~@#$%^*\(\)\"\[\]]+", "", query)
    stop_words = set(stopwords.words('english'))
    parsed_str = nlp.annotate(query, properties=props)
    parsed_dict = json.loads(parsed_str)
    lemma_list = [v for d in parsed_dict['sentences'][0]['tokens'] for k, v in d.items() if k == 'lemma']
    filtered_lemmas = [w for w in lemma_list if not w in stop_words]
    if m != None:  # AND pattern
        return multiple_key_intersect_query(trie, filtered_lemmas)
    else:
        if len(filtered_lemmas) == 0:
            import random
            return [i for i in random.shuffle(trie.get_posting_list('boy')[1].get_list())][0:32]
        return union_rank_query(trie, filtered_lemmas)

def union_rank_query(trie, words):
    candidate = [0 for i in range(262144)]
    cnt = 0
    for w in words:
        cnt += 1
        s, plist = trie.get_posting_list(w)
        if s == 0:
            continue
        s = 5 if w in ['boy', 'girl', 'cat', 'car', 'dog'] else s
        for i in range(plist.size):
            candidate[plist.elements[i].val] += 20 + s
    candidate = [(i, j) for i, j in enumerate(candidate) if j > 0]
    candidate = [i for i, j in sorted(candidate, key=lambda x: (-x[1], x[0]))]
    return candidate[0:32] if len(candidate) > 32 else candidate

def multiple_key_intersect_query(trie, words):
    plists = []
    for w in words:
        s, plist = trie.get_posting_list(w)
        if s == 0:
            # word not found
            return []
        plist.init_pointer()
        plists.append(plist)
    return comp_intersection(plists)

data_path = osp.join(osp.join('..', '..'), 'data')
trie = tr.Trie()
trie.build(tr.readin_inverted_index(osp.join(data_path, 'inverted_index_1203')))
