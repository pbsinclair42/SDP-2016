"""from multiprocessing import Process, Pipe
import random
import time
def worker(conn):
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

        """

import multiprocessing
import time

def wait_for_event(e):
    """Wait for the event to be set before doing anything"""
    while True:
        print 'wait_for_event: starting'
        e.wait()
        print 'wait_for_event: e.is_set()->', e.is_set()
        time.sleep(3)
#def wait_for_event_timeout(e, t):
#    """Wait t seconds and then timeout"""
#    while True:
#        print 'wait_for_event_timeout: starting'
        #e.wait(t)
        #print 'wait_for_event_timeout: e.is_set()->', e.is_set()


if __name__ == '__main__':
    e = multiprocessing.Event()
    w1 = multiprocessing.Process(name='block', 
                                 target=wait_for_event,
                                 args=(e,))
    w1.start()

    print 'main: waiting before calling Event.set()'
    time.sleep(3)
    print 'main: slept'
    e.set()
    print 'main: event is set'