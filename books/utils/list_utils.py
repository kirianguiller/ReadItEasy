def argmax_list(l):
    '''function that find the argmax in a list
    !!! Be careful, if 2 elements are equally max, then the function
    will return the first one in the list'''
    index, max_val = -1, -1
    for i in range(len(l)):
        if l[i] > max_val:
            index, max_val = i, l[i]
    return(index)