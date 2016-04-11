class ArrayQueue():

    def __init__(self, max_size):
        self.max_size = max_size
        self.b = -1
        self.L = [-1] * self.max_size
        self.size = 0


    # Insert an element 'x' into the queue
    def insert(self, x):

        if self.size < self.max_size:
            self.L[self.b + 1] = x
            self.b += 1
            self.size += 1

        else:
            e = self.end()
            self.L[e] = x
            self.b = e


    # Simple print for sanity checking
    def print_queue(self):
        e = self.end()
        print "B: ", self.b
        print "E: ", e
        print "Whole Q: ", self.L
        print self.L[e:] + self.L[:e]

    # Check if the queue is full
    def full(self):
        return self.size == self.max_size

    # Returns the index where the queue ends
    def end(self):
        if self.full():
            e = (self.b + 1) % self.max_size
        else:
            e = 0
        return e


    # Get the element index-th element from the queue
    def get(self, index):
        que_index = (self.b - index) % self.max_size
        return self.L[que_index]

    # Returns the most recently inserted element
    def getLeft(self):
        if self.size == 0:
            return None
        return self.get(0)

    # Returns the least recently inserted element
    def getRight(self):
        if self.size == 0:
            return None
        return self.get(self.size - 1)

    def getMaxSize(self):

        return self.max_size


    # Returns items from the ArrayQueue presented as a List object
    def iteritems(self):
        e = self.end()
        tmpL = self.L[e:self.size] + self.L[:e]
        tmpL.reverse()
        return tmpL

