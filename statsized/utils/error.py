class NetworkException(Exception):
    def __init__(self, desc):
        super.__init__(self, desc)
