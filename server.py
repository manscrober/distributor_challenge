#!/usr/bin/env python3

import flask
from flask import request
import requests
import marshal,types
import pickle
import sys,getopt
import time
import concurrent.futures

id=0
executor=None


app=flask.Flask(__name__)

@app.route("/distribute",methods=["POST"])
def distribute():
    global id,executor # id is unused, I left it because I ran the load tests with it still being there

    #get the raw data from the req
    argstring=request.data 

    #load it into a python tuple 
    args_tuple=pickle.loads(argstring)

    #unpack the tuple int individual strings
    (func_code_str,args_obj_str,kwargs_obj_str)=args_tuple

    #convert func to bytecode and load it as a named function
    func_code=marshal.loads(func_code_str)
    func=types.FunctionType(func_code,globals(),"func"+str(id))
    
    #load function arguments
    args_obj=pickle.loads(args_obj_str)
    kwargs_obj=pickle.loads(kwargs_obj_str)
    id+=1

    #start execution and await result
    future=executor.submit(func,*args_obj,**kwargs_obj)
    
    #note that technically flask already uses a thread per req, we use the threadpool to limit workers

    #await execution and return the result
    return_value=future.result()
    return pickle.dumps(return_value)
    

#this main function is only here so that one can easily specify the number of workers at launch
#e.g. server.py -n 120
def main(argv):
    global executor
    num_workers=1
    opt,args=None,None
    try:
        opts, args = getopt.getopt(argv,"hn:",["num_workers="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('server.py -n <num_workers>')
            sys.exit()
        elif opt in ("-n", "--num_workers"):
            num_workers=int(arg)
    executor=concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)
    app.run()
if __name__=="__main__":
    main(sys.argv[1:])
