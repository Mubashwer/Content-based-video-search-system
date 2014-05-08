#
# Test harness for COMP10001 Project 2, 2013s1
#
# Author: Tim Baldwin
#
# Date: 5/5/13
#
#
# THERE SHOULD BE NO NEED TO MODIFY THIS CODE IN ANY WAY; THE ORIGINAL
# VERSION OF THE CODE WILL BE USED FOR TESTING, AND ANY LOCAL CHANGES YOU
# MAKE TO THE CODE WILL NOT BE REFLECTED IN OFFICIAL TESTING
#

import getpass,sys

try:
    code = getpass.getuser()  # get the user name
    submission = __import__(code)  # import the file `USERNAME.py`
    import tests  # import the file `tests.py`

# exit if one of the above statements doesn't execute properly, presumably because `USERNAME.py` and `USERNAME-tests.py` didn't import properly
except ImportError as detail:
    print("ERROR: {}".format(detail))
    raise ImportError
except Exception as detail:
    print("ERROR: {}".format(detail))
    raise detail
    
    
EPSILON = 1.0E-5  # used to test the equality of floats -- if the absolute difference between floats is less than this value,
                  # consider them to be identical






####################################################################################
#
# name: test()
#
# synposis: run the tests for the supplied function name, and check the outputs against those in `test`
# input(s): the function name to be tested (str)
# output(s): print the tests that are tried, and if unsuccessful, the correct value vs. returned value
#

def test(funct_name):
    # print out the names of functions which can be tested in `funct_name` is not in `tests`, and exit
    if funct_name not in tests.test_cases:
        print "ERROR: '{0}' is not a recognised function name; select from: {1}".format(funct_name,str(tests.test_cases.keys()))
        return
    
    # run test (using valid function name)
    print "Testing the {0} function ...\n".format(funct_name)
    correct = 0  # number of tests passed
    
    # run the user-defined function with each of the sets of arguments provided in `tests`, and chech that the
    # output is correct
    for test in tests.test_cases[funct_name]:
        print "  testing {0} ...".format(test[0]),
        userval = eval(test[0])  # run the function with the supplied set of arguments (take the string and execute it)
        
        # if the returned value is correct, increment `correct` and print a congratulatory print statement
        if test_equal(userval,test[1]):
            correct += 1
            print "passed"
            
        # if the returned value is *in*correct, print diagnostics
        else:
            print "failed"
            print "    * expected value = {0}".format(test[1])
            print "    * returned value = {0}".format(userval)
    
    # print the overall number of tests passed vs. attempted    
    print "\n{0}/{1} tests passed for {2}".format(correct,len(tests.test_cases[funct_name]),funct_name)

#   
# end test()    
####################################################################################
    
   



def test_index(csv_file,val):
    import cPickle
    picklefile = "test.pkl"
    submission.make_index(csv_file,picklefile)
    pkl_file = open(picklefile, "rb")
    tf = cPickle.load(pkl_file)
    df = cPickle.load(pkl_file)
    try:
        return eval(val)
    except:
        return






####################################################################################
#
# name: test_equal()
#
# synposis: test for equality between two arguments of arbitrary type, mainly to check
#   to check to see if two float values are "close enough"; for tuples and lists, recursively
#   check the contents, and fail if one or more elements doesn't match
# input(s): two arguments of arbitrary type
# output(s): Boolean evaluation of the equality of the two arguments
#

def test_equal(a,b):
    # the type of the arguments must be the same
    if type(a) != type(b):
        return False
    
   # ints and strs must be identical in value
    if (type(a) == int == type(b)) or (type(a) == str == type(b)) or (type(a) == bool == type(b)):
        return a == b
    
    # floats can differ by up to `EPSILON` and still be considered identical
    elif type(a) == float == type(b):
        return abs(a - b ) < EPSILON
    
    # tuples/lists must be of the same length, and each element must be equal (evaluated recursively)
    elif (type(a) == tuple == type(b)) or (type(a) == list == type(b)):
        if len(a) != len(b):
            return False
        retval = True
        for i,j in zip(a,b):
            retval = retval and test_equal(i,j)
        return retval

#  
# end test_equal()   
####################################################################################
    



# code used to run the script from the command-line (for Tim's sanity in code development!)

if __name__=="__main__":
    for fun_name in tests.test_cases.keys():
        test(fun_name)
