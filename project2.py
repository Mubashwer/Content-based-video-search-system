#------------------------------------------------------------------------------
# Name:        mskh.py
# Purpose:     Project 2
# Author:      Mubashwer Salman Khurshid (ID: 601738)
# Created:     29/04/2013
#------------------------------------------------------------------------------

from collections import defaultdict
import cPickle, csv, urllib
from math import floor, log10, log, fsum, sqrt, pow as power
import matplotlib as mpl
mpl.use('Svg')
import matplotlib.pyplot as plt
from operator import itemgetter


def extract_words(text):
    '''This is a supporting function used to extract words from text.
    Trailing punctuations are stripped.'''    
    word_list = text.lower().split()

    #Trailing punctuations are stripped.
    for index in range(len(word_list)):
        word_list[index] = word_list[index].strip(",.:;!?-'\"()[]{}")

    #Empty items are removed from list if present.
    try:
        while True:
            word_list.remove('')
    except ValueError:
        return word_list


def url_order(url_list):
    '''This is a supporting function which returns a dictionary
    of urls with their order as  values. The order is relative and
    is reversed. url_list must be a sorted list.'''
    order_url = defaultdict(int)
    url_list.sort()

    #the first url has the highest order
    #and the last url has the least order
    max_order = len(url_list)
    for url in url_list:
        order_url[url] = max_order
        max_order -= 1

    return order_url

            
def make_index(datafile, picklefile):
    '''It takes two arguments:
    (1) datafile stipulating the name of a file containing video descriptions
    (2) picklefile stipulating the name of a cPickle file to store the
    output of the function. The picklefile stores two dictionaries.
    First dictionary contains url as keys and word frequencies for the
    given url as values. The second dictionary contains a dictionary of total
    word frequencies of the entire collection.'''

    data = csv.reader(open(datafile))
    dict_url = {} #first dictionary to be pickled
    dict_words = defaultdict(int) #dictionary of words to scores of a url
    dict_total_words = defaultdict(int) #second dictionary to be pickled
    link = "http://www.youtube.com/watch?v="
    data_2d = sorted(data) #data is sorted so the same urls are together
    size = len(data_2d)
    index = 1

    for line in data_2d:
        words = extract_words(line[7])
        for word in words:
            dict_words[word] += 1 #appends dictionary of words frequencies
            
        #if the next ID or start time is different, dictionary of
        #word frequencies is added to the dictionary of urls
        if(index >= size or line[0] != data_2d[index][0]\
           or line[1] != data_2d[index][1]):
            new_url = True
            dict_words["__TOTAL__"] = sum(dict_words.values())
            dict_url[link+line[0]+"#t="+line[1]+"s"] = dict(dict_words)

            #when the dictionary data for a single url is completed
            #the dictionary of number of occurences of word is
            #updated
            for word in dict_words:
                dict_total_words[word] += 1           
            dict_words.clear() #cleared for next url

        index += 1

    dict_total_words["__TOTAL__"] = len(dict_url) #total number of urls

    with open(picklefile, "wb") as pFile:
        cPickle.dump(dict_url, pFile)
        cPickle.dump(dict(dict_total_words), pFile)

    del data_2d
    dict_total_words.clear()
    dict_url.clear()
    return

def word_freq_graph(index_fname, graph_fname, word):
    '''It takes three arguments:
    (1) index_fname stipulating the name of a pickle file
    containing an index of descriptions,
    (2) graph_fname stipulating a file name in which to
    store the output graph, and
    (3) word stipulating a word to generate the graph for.
    It generates a histogram of word frequencies for word
    in index_fname.'''

    with open(index_fname, "rb") as pFile:
        dict_url = cPickle.load(pFile)
        dict_total_words = cPickle.load(pFile)

    max_freq = 0
    freq_zero = len(dict_url) - dict_total_words[word]
    for url in dict_url:
        #Finds the maximum frequency of given word for given video
        if word in dict_url[url] and dict_url[url][word] > max_freq:
            max_freq = dict_url[url][word]

    video_num_list = [freq_zero] #list ofnumber of videos
    freq_list = [0] #list of frequency of given word in ascending order
            
    video_num = 0
    #creates list of frequencies and corresponding number of videos
    for freq in xrange(1,max_freq + 2):
        video_num = 0
        for url in dict_url:
            if (word in dict_url[url] and dict_url[url][word] == freq):
                    video_num += 1
        
        freq_list.append(freq)
        video_num_list.append(video_num)

    #plots histogram of word frequencies and number of videos
    plt.hist(freq_list, max_freq+2, range = [-0.5,max_freq+1.5],\
             weights = video_num_list, facecolor="green", log = True)
    plt.axis([-0.5, max_freq+1.5, 10**-1,\
              10**floor(log10(max(video_num_list))+1)])

    #custom tick labelling   
    def custom(x, pos):
        if (x - int(x) != 0.0):
            return ""
        elif (x == 10**-1):
            return ""
        return "${0}$".format(int(x))

    ax = plt.gca()
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(custom))
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(custom))
    plt.xlabel('Frequency of word in descriptions for a given video')
    plt.ylabel('Number of videos')
    plt.title('Histogram of word frequencies in video description')
    plt.grid(True)
    plt.draw()
    plt.savefig(graph_fname, format = "svg")
    plt.clf()
    return
    
    
def single_word_search(index_fname, word):
    '''It takes two arguments:
    (1) index_fname stipulating the name of a pickle file containing an
    index of descriptions, and (2) a single word word (in the form of a
    string) and returns a list of video URLs ranked in decreasing order
    of relevance score.'''
    urls = []
    score_dict = {} #dictionary of url to tuple of score and order 

    with open(index_fname, "rb") as pFile:
        dict_url = cPickle.load(pFile)

    order_url = url_order(dict_url.keys())

    #score and order of url is added to the url dictionary
    #order of url is required for sub-ranking
    for url in dict_url:
        if word in dict_url[url]:
            fdt = float(dict_url[url][word])
            score_dict[url] = (fdt/dict_url[url]["__TOTAL__"], order_url[url])

    #urls are sorted in decreasing order of score
    #and subranked in increasing order of url
    urls = [item[0] for item in sorted(score_dict.items(),\
            key = itemgetter(1), reverse = True)]
    return urls

    
def search(index_fname, query):    
    '''It takes two arguments:
    (1) index_fname stipulating the name of a pickle file containing an
    index of descriptions, and (2) a query (in the form of a
    string) and returns a list of video URLs ranked in decreasing order
    of relevance score.'''
    
    query_list = extract_words(query)

    with open(index_fname, "rb") as pFile:
        dict_url = cPickle.load(pFile)
        ft = cPickle.load(pFile)

    N = float(len(dict_url.keys()))
    word_scores = {} #words to scores dictionary
    url_scores = {} #url to dictionary of words to scores
    finalscore_dict = {} #url to tuple of query score and order of url
    total = len(dict_url.keys())
    url_list = []

    #generates a list of url in which at least one word of the query
    #is present
    for url in dict_url:
        for word in query_list:
            if word in dict_url[url]:
                url_list.append(url)
                break
        
    #relative reversed ascii order of urls is generated
    order_url = url_order(url_list)

    #for each url, a dictionary of words to scores is generated
    #and it is added to a dictionary of urls
    index = 1
    for url in url_list:
        fd = dict_url[url]["__TOTAL__"]
        for word in query_list:
            if(word in dict_url[url]):
                fdt = float(dict_url[url][word])
            else:
                fdt = 0
            score = (fdt / fd) * log(N / (ft[word] + 1))
            #if word is repeated, a number is added to it
            #so that it can be treated as a different word
            if word in word_scores:
                word_scores[word + str(index) + '.'] = score
                index += 1
            else:
                word_scores[word] = score
        url_scores[url] = dict(word_scores)
        word_scores.clear()

    score_sum = 0.0 #sum of scores of relevant words of url
    square_scores = []#list of squared scores of relevant of url
    sum_of_squares = 0.0 #sum of squres of scores of relevant words of url

    #generates a dictionary of url to a tuple of query score and order
    for url in url_list:
        score_sum = fsum(url_scores[url].values())
        square_scores = [power(num,2) for num in url_scores[url].values()]
        sum_of_squares = fsum(square_scores)
        finalscore_dict[url] = (score_sum/sqrt(sum_of_squares), order_url[url])

    #sorts url by query score and sub-sorts by order of url   
    urls = [item[0] for item in sorted(finalscore_dict.items(),\
            key = itemgetter(1), reverse = True)]
    return urls
    

def rr(query,doc_ranking,qrels):
    '''It is a function that takes three arguments:
    (1) query containing a search query,
    (2) doc_ranking containing a (ranked) list of documents for query,
    (3) qrels stipulating the name of a file containing queries with relevant
        video IDs and start times.
    It returns the "reciprocal rank" (RR) for doc_ranking based on qrels.'''

    qrel_lines = open(qrels, "rb").readlines()
    url_list = []
    url = "http://www.youtube.com/watch?v="

    #Creates a list of URLs from qrels relevant for given query
    for line in qrel_lines:
        data = line.split(',')
        if(data[0].strip(",.:;!?-'\"()[]{}") == query):
            url_list.append(url + data[1] + "#t=" + data[2].rstrip('\n') + 's')
            
    #If URL from doc_ranking is found in the url_list, RR is returned.
    for index in xrange(len(doc_ranking)):
        if(doc_ranking[index] in url_list):
            return (1.0 / (index + 1))
    return 0

            
def batch_evaluate(index_fname, queries, qrel, filename):
    '''It that takes a pre-computed index index_fname, a list of queries
    queries (made up of string-based queries), a file containing relevance
    judgements qrel, and the name of a file to save the HTML output to,
    and generates a rr vs queries graph, mrr vs length of queries graph,
    an html page with above mentioned graphs and a table of query, rr and
    number of results.'''

    length = len(queries);
    results = []
    rr_list = []
    row_headings = ["Queries", "No. of Results", "RR"]
    
    #creates list of number of results and rr
    for query in queries:
        doc_ranking = search(index_fname, query)
        results.append(len(doc_ranking))
        rr_list.append(rr(query,doc_ranking,qrel))
        del doc_ranking

    #plots bar graph of rr vs queries
    x = range(len(queries))
    heights = rr_list
    plt.bar(x, heights, color = "green", align = "center")
    ax = plt.gca()
    ax.set_xticks(x)
    ax.set_xticklabels(queries)
    plt.axis([-0.5, max(x)+0.5, 0.0, 1.1])
    plt.xlabel('Queries')
    plt.ylabel('Reciprocal rank (RR)')
    plt.title('Bar graph of reciprocal rank (RR) of queries')
    plt.grid(True)
    plt.draw()
    plt.savefig('mskh-rr.svg', format = "svg")
    plt.clf()
    mrr_dict = defaultdict(int)
    rr_num = defaultdict(int)

    #a list of tuples of queries and RR values is
    #created in order to create a dictionary of
    #of rr with length as key and sum of rr as values
    #Another dictionary, rr_num creates a dictionary
    #with length as key and number of instances
    #of query with such length as values.
    query_rr = zip(queries, rr_list)
    for entry in query_rr:
        mrr_dict[len(entry[0].split())] += entry[1]
        rr_num[len(entry[0].split())] += 1.0

    #mrr values are calculated by diving the sum of
    #rr by the number of instances of rr for
    #query with unique length in terms of number of
    #words
    for key in mrr_dict:
        mrr_dict[key] /= rr_num[key]

    #list of different lengths and mrr are created
    #needed to calculate x values and height values
    #for graph
    length_list = []
    mrr_list = []
    for item in sorted(mrr_dict.items()):
        length_list.append(item[0])
        mrr_list.append(item[1])
    
    #plots graph of MRR vs length of queries in terms of words
    x = range(len(length_list))
    heights = mrr_list
    plt.bar(x, heights, color = "green", align = "center")
    ax = plt.gca()
    ax.set_xticks(x)
    ax.set_xticklabels(length_list)
    plt.axis([-0.5, max(x)+0.5, 0.0, 1.1])
    plt.xlabel('Length of queries (in terms of number of words)')
    plt.ylabel('Mean Reciprocal rank (RR)')
    plt.title('Bar graph of mean reciprocal rank (MRR) of subset of'\
              ' queries\n having different lengths')
    plt.grid(True)
    plt.draw()
    plt.savefig('mskh-mrr.svg', format = "svg")
    plt.clf()
    
    mrr = fsum(rr_list)/len(rr_list)
    
    #create list of lists of data for table
    table = []
    table.append(queries + [''])
    table.append(results + [''])
    table.append(rr_list + [mrr])
    
    #determines column span
    span = 0
    while(span <= len(rr_list)):
        span += 1

    #text is the html code to be written in html file
    text = "<!DOCTYPE html>\n<html>\n"
    text += "<head>\n<title>Statistics of Search Results</title>\n</head>\n"
    text += '<body>\n<h1>Statistics of Search Results</h1>'

    #writes code for table and stores it as string in text
    text += '<h2>Table of queries and reciprocal ranks (RR): </h2>'
    text += '<table border="1" bordercolor="Indigo" style='
    text +=  '"background-color:Black"cellpadding="3" cellspacing="3"><tr>'

    #writes column heading namely mrr
    text += '<th colspan="{}" bgcolor= "Brown"></th>'.format(span)
    text += '<th bgcolor= "Brown">Mean RR (MRR)</th></tr>'

    row_index = 0    
    #writes each row of table
    for row in table:
        string = '<tr><th bgcolor= "Silver">{}</th>'
        text += string.format(row_headings[row_index])
        row_index += 1
        for entry in row:
            text += '<td bgcolor= "MintCream">{}</td>'.format(entry)
        text += '</tr>'
    text += '</table>'

    text += '<h2>Graphs of reciprocal ranks and mean reciprocal '
    text += 'ranks of queries:</h2>' 
    text += '<img src="mskh-rr.svg"><img src="mskh-mrr.svg">'
    text += '\n</body>\n</html>'
         
    #saves code stored in text in html file
    with open(filename, "w") as html_file:
        html_file.write(text)

    return

def translation(word, data, max_nodes, current_node, path, lang = "English"):
    '''It is a supporting function which generates a list of tuples
    expanded from a word. The tuple consists of the word and the
    number of nodes. Path makes sure that none of the words come back
    to the original word.'''
    trans_tuple = []

    if current_node > max_nodes:
        return []
    for line in data:
        if word in line:
            #if an english target word is found, it is added
            if(line[1] == word and line[2] == "English"\
               and (line[3],line[0]) not in path and lang == line[0]):
                    trans_tuple += [(line[3], current_node)]
            #same as above
            elif(line[3] == word and line[0] == "English"\
                 and (line[1],line[0]) not in path and  lang == line[2]):
                    trans_tuple += [(line[1], current_node)]
            #if the word is found but target word is not english
            #node and path are updated and the translation
            #function is called for the target word
            elif(line[1] == word and (line[3],line[2]) not in path and\
                 lang == line[0]):
                    trans_tuple += translation(line[3],data,max_nodes,\
                        current_node+1, path + [(line[1], line[0])],line[2])
            #same as above
            elif(line[3] == word and (line[1],line[0]) not in path and\
                 lang == line[2]):
                    trans_tuple += translation(line[1],data,max_nodes,\
                        current_node+1, path + [(line[3],line[2])],line[0])   

    return trans_tuple

def shortest_path(trans_tuple):
    '''This is a supporting function which generates
    a list of tuples containg expanded query with the
    smallest number of nodes.'''
    #Possible duplicates are removed
    trans_tuple = sorted(set(trans_tuple))
    
    delete_list = []
    previous = ('',0)

    #Duplicate words with higher number
    #of nodes are to be removed. The list is
    #sorted so if word appears more than
    #once, it is to be removed.
    for entry in trans_tuple:
        if entry[0] == previous[0]:
            delete_list += [entry]
        previous = entry

    for entry in delete_list:
        trans_tuple.remove(entry)
    return trans_tuple

def bonus(index_fname, transfile, query, max_nodes = 4):    
    '''It takes four arguments - (1) index_fname stipulating the
    name of a pickle file containing an index of descriptions;
    (2) transfile stipulating the name of a file containing translations;
    (3) query containing the (English) search query; and
    (4) max_nodes which stipulates the maximum number of nodes
    in a translation path (with a default value of 4) -
    and returns a list of video URLs ranked in decreasing order
    of "relevance score"'''
    query_list = extract_words(query)
    data = list(csv.reader(open(transfile)))

    with open(index_fname, "rb") as pFile:
        dict_url = cPickle.load(pFile)
        ft = cPickle.load(pFile)

    N = float(len(dict_url.keys()))
    word_scores = {} #words to scores dictionary
    url_scores = {} #url to dictionary of words to scores
    finalscore_dict = {} #url to tuple of query score and order of url
    total = len(dict_url.keys())
    url_list = []

    #the query is expanded
    expanded_list = []
    for word in query_list:
        word_list = translation(word,data,max_nodes,2,\
                                [(word,"English")]) + [(word,1)]
        word_list = shortest_path(word_list)     
        expanded_list += word_list
    
    #generates a list of url in which at least one word of the query
    #is present
    for url in dict_url:
        for entry in expanded_list:
            if entry[0] in dict_url[url]:
                url_list.append(url)
                break
        
    #relative reversed ascii order of urls is generated
    order_url = url_order(url_list)

    #for each url, a dictionary of words to scores is generated
    #and it is added to a dictionary of urls
    index = 1
    for url in url_list:
        fd = dict_url[url]["__TOTAL__"]
        for entry in expanded_list:
            if(entry[0] in dict_url[url]):
                fdt = float(dict_url[url][entry[0]])
            else:
                fdt = 0
            score = (1.0 / (power(entry[1],2))) *\
                    (fdt / fd) * log(N / (ft[entry[0]] + 1))
            #if word is repeated, a number is added to it
            #so that it can be treated as a different word
            if entry[0] in word_scores:
                word_scores[entry[0] + str(index) + '.'] = score
                index += 1
            else:
                word_scores[entry[0]] = score
        url_scores[url] = dict(word_scores)
        word_scores.clear()

    score_sum = 0.0 #sum of scores of relevant words of url
    square_scores = []#list of squared scores of relevant of url
    sum_of_squares = 0.0 #sum of squres of scores of relevant words of url

    #generates a dictionary of url to a tuple of query score and order
    for url in url_list:
        score_sum = fsum(url_scores[url].values())
        square_scores = [power(num,2) for num in url_scores[url].values()]
        sum_of_squares = fsum(square_scores)
        finalscore_dict[url] = (score_sum/sqrt(sum_of_squares), order_url[url])

    #sorts url by query score and sub-sorts by order of url   
    urls = [item[0] for item in sorted(finalscore_dict.items(),\
            key = itemgetter(1), reverse = True)]
    return urls
