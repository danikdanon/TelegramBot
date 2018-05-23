def dictCurrNext(words):

    dict = {}

    for i in range(len(words)-1):
        curr = words[i]
        next = words[i+1]

        if curr in dict:
            if next in dict[curr]:
                dict[curr][next]+=1
            else:
                dict[curr][next] = 1
        else:
            dict[curr] = {}
            dict[curr][next] = 1

    return dict




def dictCurrPrev(words):
    dict = {}

    for i in range(1,len(words)):
        curr = words[i]
        prev = words[i - 1]

        if curr in dict:
            if prev in dict[curr]:
                dict[curr][prev] += 1
            else:
                dict[curr][prev] = 1
        else:
            dict[curr] = {}
            dict[curr][prev] = 1

    return dict



def wordCntDict(words):

    dict = {}
    for word in words:
        if word in dict:
            dict[word] += 1
        else:
            dict[word] = 1

    return dict
