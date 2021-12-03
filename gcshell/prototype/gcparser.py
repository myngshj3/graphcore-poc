
class CommandParser:

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        command = args[0]
        graph = args[1]
        scene = args[2]
        queue = args[3]
        self.parse(command, graph, scene, queue)

    def parse(self, command, graph, scene, queue):
        pass