
class GraphCoreError(Exception):
    def __init__(self, text="", exception: Exception=None):
        super(Exception, self).__init__()
        self.text = text
        self.exception = exception
