#!/usr/bin/env python3

import marshal
import pickle
import requests
import configparser

config=configparser.ConfigParser()
config.read("distributor.conf")
api_host=config.get("API","API_HOST_URL")
class RemoteWorkload:
    def __init__(self,*args,**kwargs):
        #copy all the arguments
        self.__dict__.update(kwargs)
        #set default post function
        #I made the post function customizable for the load tests
        if not hasattr(self,"postfunction"):
            self.postfunction=requests.post

    def send_func_and_args_to_host(self,code,args,kwargs):
        #convert the argument tuple to binary string
        myrequestdata=pickle.dumps((code,args,kwargs))
        
        #call the custom post function with the config-specified host and the serialized data
        return_value=self.postfunction(self.host,data=myrequestdata)
        return pickle.loads(return_value.content)

    def run(self):
        #convert code to bytecode, serialized args/kwargs
        #I chose to serialize twice because you can't pickle the function code(I think)
        code=marshal.dumps(self.func.__code__)
        args=pickle.dumps(self.args)
        kwargs=pickle.dumps(self.kwargs)
        return self.send_func_and_args_to_host(code,args,kwargs)



#this parameter is only there for load tests
def compute_this(postfunction):
    global api_host
    def computer(func):
        def wrapper(*args,**kwargs):
            task=RemoteWorkload(postfunction=postfunction,func=func,host=api_host,args=args,kwargs=kwargs)
            return task 
        return wrapper
    return computer


