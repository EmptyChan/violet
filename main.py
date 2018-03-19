# -*- coding: utf-8 -*- 
"""
 Created with IntelliJ IDEA.
 Description:
 User: jinhuichen
 Date: 3/19/2018 11:35 AM 
 Description: 
"""
from mrq.job import queue_job



if __name__ == '__main__':
    res = queue_job('tasks.general.Add', {"a": 1, "b": 2}, queue='simple')
    print(res)