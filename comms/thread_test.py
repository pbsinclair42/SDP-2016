from multiprocessing import Process, Pipe
import random
import time
# 1. 

def worker(conn):
    """thread worker function"""
    start = time.time()
    while True:
    	if conn.poll():
	    	print "Receiving"
	    	x = conn.recv()
    		print "Received:", x
    		start = time.time()
    	elif time.time() - start > 5:
    		print "Exiting"
    		return

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=worker, args=(child_conn, ))
    p.start()
    l = []
    for i in range (0, 10):
    	l.append(raw_input())
    parent_conn.send(l)
    p.join()

        