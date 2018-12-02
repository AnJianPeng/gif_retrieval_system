import tretrieval.skip_list as sl

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
            break;
        if target == current_target:
            intr_sect.append(current_target)
            print(current_target)
            target += 1

    return intr_sect

if __name__ == '__main__':
    def test_comp_intersection():
        postings = [[1,2,4,6,8,11,12,19,23,33,34,37,51], [1,3,4,5,11,13,17,19,23,24,25,35,36,37,51,52,67], [1,3,4,9,11,16,18,19,22,24,25,37,42,48,51,52,89]]
        lists = [sl.SkipList(i) for i in postings]
        print(comp_intersection(lists))

    test_comp_intersection()
