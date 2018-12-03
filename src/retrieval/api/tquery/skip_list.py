import math

'''
Python list based skip-list for efficient target searching
Not support efficient insert and no random since the underlying is array instead of linked list
'''


class SkipListNode:
    next = []
    val = 0

    def __init__(self, val):
        self.val = val


class SkipList:
    size = 0
    layer_cnt = 0
    elements = []

    def __init__(self, indexList):
        self.size = len(indexList)
        self.layerCnt = math.floor(math.log(self.size, 2))
        self.elements = [SkipListNode(i) for i in indexList]
        self.elements[0].next = [int(pow(2, i)) for i in range(self.layerCnt)]
        for i in range(1, self.size):
            self.elements[i].next = [
                (j + int(pow(2, k)) if j + int(pow(2, k)) <= self.size else self.size) if j == i else j for k, j in
                enumerate(self.elements[i - 1].next)]
        self.cur_subscript = 0

    def init_pointer(self):
        self.cur_subscript = 0

    def get_current_val(self):
        return self.elements[self.cur_subscript].val

    # return the smallest element that is larger than or equal to target
    def forward(self, target):
        if self.cur_subscript == self.size:
            return -1
        if self.elements[self.cur_subscript].val >= target:
            return self.elements[self.cur_subscript].val
        i = self.layerCnt - 1
        while i >= 0:
            next_subscript = self.elements[self.cur_subscript].next[i]
            if next_subscript >= self.size:
                pass
            elif self.elements[next_subscript].val == target:
                self.cur_subscript = next_subscript
                return target
            elif self.elements[next_subscript].val < target:
                self.cur_subscript = next_subscript
                return self.forward(target)
            else:
                assert self.elements[next_subscript].val > target
            i -= 1
        self.cur_subscript += 1
        return -1 if self.cur_subscript == self.size else self.elements[self.cur_subscript].val

    def is_finished(self):
        return self.cur_subscript == self.size

    # Print details of the data structure, for debug use
    def print(self):
        for i in range(self.size):
            print(str(i) + '\t' + str(self.elements[i].val) + '\tLayer=' + str(self.layerCnt) + '\t[' + ','.join(
                [str(t) for t in self.elements[i].next]) + ']')


if __name__ == '__main__':
    def testSkipList():
        posting = [1, 2, 4, 6, 8, 12, 19, 23, 33, 34, 37, 51]
        sample = SkipList(posting)
        sample.print()
        print([sample.forward(i) for i in [4, 5, 6, 17, 18, 19, 37, 53]])
        print("Finished? " + str(sample.is_finished()))

    testSkipList()
