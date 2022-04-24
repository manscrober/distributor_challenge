#!/usr/bin/env python3

from distribute_challenge import compute_this
import time
import threading


from locust import HttpUser, task
class HelloWorldUser(HttpUser):
    #outer function,hello_world test and class are only there for the locust load tests
    #technically, this would be enough(if the distribute_challenge code was adapted to remove compute_this param):
    #@compute_this()
    #def func(x):
    #   time.sleep(x)
    #   return x*x
    #assert func(2).run()==4
    def get_function_with_self_client_post(self):
        @compute_this(postfunction=self.client.post)
        def func(x):
            time.sleep(x)
            return x*x
        return func
    @task
    def hello_world(self):
        func=self.get_function_with_self_client_post()
        out=func(2).run()
        assert out==4

