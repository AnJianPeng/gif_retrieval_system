import json
import math
from nltk.corpus import stopwords
from stanfordcorenlp import StanfordCoreNLP

def fetchData(fprefix):
    desc = []
    for datafile in ["boy.csv", "car.csv", "cat.csv", "dog.csv", "girl.csv"]:
        fpath = fprefix + datafile
        dfile = open(fpath, 'r')
        data = dfile.read().split('\n')
        dfile.close()
        for line in data:
            if len(line) == 0:
                continue
            items = line.split(',')
            index = items[0]
            description = items[2]
            desc.append((index, description))
    return desc


def build(desc):
    iindex = dict()
    dfreq = dict()
    lemmatized_desc = []
    from nltk.corpus import stopwords
    from stanfordcorenlp import StanfordCoreNLP
    nlp = StanfordCoreNLP('http://localhost', port=9000, timeout=30000)
    props = {'annotators': 'pos,lemma',
             'pipelineLanguage': 'en',
             'outputFormat': 'json'}
    stop_words = set(stopwords.words('english'))

    for record in desc:
        description = record[1]
        gid = record[0]
        # Normalization
        parsed_str = nlp.annotate(description, properties=props)
        parsed_dict = json.loads(parsed_str)
        lemma_list = [v for d in parsed_dict['sentences'][0]['tokens'] for k, v in d.items() if k == 'lemma']
        filtered_lemmas = [w for w in lemma_list if not w in stop_words]
        # Build & Statistic
        for w in set(filtered_lemmas):
            if w not in iindex:
                iindex[w] = [gid]
            else:
                iindex[w].append(gid)
            if w not in dfreq:
                dfreq[w] = 1
            else:
                dfreq[w] += 1
        lemmatized_desc.append((gid,filtered_lemmas))
    return iindex, dfreq, lemmatized_desc

def saveLemmatizedDescription(lemmatized_desc, fpath):
    dfile = open(fpath, 'w')
    for record in lemmatized_desc:
        dfile.write(record[0] + ',' + ' '.join(record[1]) + '\n')
    dfile.close()

def saveIndexes(iindex, dfreq, n, fpath):
    dfile = open(fpath, 'w')
    for lemma in iindex:
        sorted(iindex[lemma])
        dfile.write(lemma + '\t' + str(math.log(n/dfreq[lemma], 10)) + '\t' + ','.join(iindex[lemma]) + '\n')
    dfile.close()

def writeIndexesToRedis(): #todo
    pass

if __name__ == '__main__':
    fprefix = "/path/to/data/csv/"
    l_path = "path/to/save/lemmatized/descriptions/"
    # i_path = "path/to/save/inverted-index//optional/"
    d = fetchData(fprefix)
    iindex, dfreq, lemmatized_desc = build(d)
    # saveLemmatizedDescription(lemmatized_desc, l_path)
    # saveIndexes(iindex, dfreq, len(lemmatized_desc), i_path)
