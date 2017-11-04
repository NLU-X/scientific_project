from collections import defaultdict
import re
import operator
import sys
from nltk import word_tokenize, PorterStemmer
import string 

ps = PorterStemmer()

def is_doc_present(doc_id,lst):
    for l in lst:
        if l[0] == doc_id:
            return lst.index(l)
        if doc_id < l[0]:
            return -1
    return -1
        
def add_word_to_dict(indexdict,word,doc_id,word_id):
    if indexdict[word] != -1:
        tmp_lst = indexdict[word] 
        index_to_be_inserted = is_doc_present(doc_id,tmp_lst)
        if index_to_be_inserted != -1:
            tmp_in_lst=tmp_lst[index_to_be_inserted]
            tmp_in_lst.append(word_id)
            tmp_lst[index_to_be_inserted] = tmp_in_lst
        else: 
            tmp_lst.append([doc_id,word_id])
    else: 
       indexdict[word] = [[doc_id,word_id]] 

def def_dict() :
    return -1
       
def create_positional_index(tokens):
    indexdict = defaultdict(def_dict)
    doc_id = 0
    for doc in tokens:
        word_id = 0
        for word in doc:
            add_word_to_dict(indexdict,word,doc_id,word_id)
            word_id +=  1

        doc_id += 1    
    return indexdict

def compare_document_postings(list1,list2):
    result=[]
    i=0
    j=0
    while i < len(list1) and j < len(list2):
        if (int(list1[i])+1) == list2[j]:
            result.append(list2[j])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1
    return result
    
def phrase_intersect(list1, list2):
    result=[]
    i=0
    j=0
    while i < len(list1) and j < len(list2):
        if list1[i][0] == list2[j][0]:
            tmplst = compare_document_postings(list1[i][1:],list2[j][1:])
            if len(tmplst) != 0:
                result.append(([list2[j][0]]+tmplst))
            i += 1
            j += 1
        elif list1[i][0] < list2[j][0]:
            i += 1
        else:
            j += 1
    return result
    

def get_document_id(lst):
    result = []
    for l in lst:
        result.append(l[0])
    return result
    
def search(index, query):
    result = []
    tmp_query = word_tokenize(query.translate(None, string.punctuation))
    tmp_query = [ps.stem(w) for w in tmp_query]
    if len(tmp_query) == 1 :
        if index[tmp_query[0]] != -1:
            result.append(index[tmp_query[0]]) 
    else: 
        tmp = phrase_intersect(index[tmp_query[0]],index[tmp_query[1]]) 
        for i in range(2,len(tmp_query)):
            tmp = phrase_intersect(tmp,index[tmp_query[i]])
        
        result.append(tmp)
    
    tmp_lst = []
    for r in result:
        tmp_lst = tmp_lst + get_document_id(r)
    return (list(set(tmp_lst)))    
    pass

                
def find_top_bigrams(terms, n):
    dict = defaultdict(def_dict)
    for lst in terms:
        for i in range(0,len(lst)-1):
            word = lst[i]+' '+lst[i+1]
            if dict[word] == -1: 
                dict[word] = 1
            else:
                value = dict[word]
                dict[word] = value+1

    sorted_elements = sorted(dict.iteritems(), key=operator.itemgetter(1),reverse=True)
    return sorted_elements[:n]
    pass


def main(filename, query):
    with open(filename,'r') as df :
       documents = [l.strip().translate(None, string.punctuation).encode('utf8') for l in df.read().split('\t')]
       print documents
    terms = [[ps.stem(w) for w in word_tokenize(d)] for d in documents]
    index = create_positional_index(terms)
    query = query.strip().translate(None, string.punctuation)

    results = search(index, query)

    print '\n\nQUERY:', query, '\nRESULTS:\n', '\n'.join(documents[r] for r in results)

    print '\n\nTOP 11 BIGRAMS'
    print '\n'.join(['%s=%d' % (bigram, count) for bigram, count in find_top_bigrams(terms, 11)])

  
if __name__ == '__main__':
    if len(sys.argv) < 2 :
        print("Il manque un element")

    filename = sys.argv[1]
    query = sys.argv[2]
    main(filename, query)
