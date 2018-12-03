import tquery.skip_list as sl

class TrieNode:
    valid = False
    idf_based_score = 0
    child = []

    def __init__(self):
        self.valid = False
        self.idf_based_score = 0

class Trie:
    root = TrieNode()

    def __init__(self):
        self.root = TrieNode()

    def add_word(self, w, score, posting_list):
        if w[0] < 'a' or w[0] > 'z':
            return
        current = self.root
        for char in w:
            next_id = 26 if char == '-' else ord(char)-97
            if len(current.child) == 0:
                current.child = [TrieNode() for i in range(27)]
                current.child[next_id].valid = True
            elif not current.child[next_id].valid:
                current.child[next_id].valid = True
            current = current.child[next_id]
        current.idf_based_score = float(score)
        current.posting_list = sl.SkipList(posting_list)

    def get_posting_list(self, word):
        current = self.root
        for char in word:
            next_id = 26 if char == '-' else ord(char) - 97
            if len(current.child) == 0:
                return 0, None
            if not current.child[next_id].valid:
                return 0, None
            current = current.child[next_id]
        if current.idf_based_score == 0:
            return 0, None
        return current.idf_based_score, current.posting_list

    def build(self, w_s_p_tuple_list):
        for word, score, plist in w_s_p_tuple_list:
            self.add_word(word, score, plist)

    def build2(self, w_s_p_tuple_list, score_assign):
        for word, score, plist in w_s_p_tuple_list:
            if word in score_assign:
                score = score_assign[word]
            self.add_word(word, score, plist)


# read inverted-lists from file and construct a (w, s, plist) tuple list
def readin_inverted_index(path):
    tuple_list = []
    i_file = open(path, 'r')
    data = i_file.read().split('\n')
    i_file.close()
    for line in data:
        if len(line) == 0:
            continue
        w, s, plist = line.split('\t')
        plist = [int(i) for i in plist.split(',')]
        tuple_list.append((w, s, plist))
    return tuple_list


if __name__ == '__main__':
    def test_trie_build(tuples):
        trie = Trie()
        trie.build(tuples)
        score, plist = trie.get_posting_list('near')
        print(score)
        if score != 0:
            plist.print()

    tuples = readin_inverted_index("/path/to/inverted/index/file/")
    test_trie_build(tuples)
