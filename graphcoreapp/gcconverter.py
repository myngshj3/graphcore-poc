

import networkx as nx
import yaml
import sys
import json
from graphcore.gcconvert import GCYamlLoader, GCGraphLoader, GCConverter
import traceback


def main():
    try:
        if len(sys.argv) < 3:
            sys.stderr.write("file not specified\n")
            sys.stderr.write("usage:\n")
            sys.stderr.write("  gcconvert <old-file> <output-file>\n")
            return
        loader = GCYamlLoader()
        G = loader.load(sys.argv[1])
        converter = GCConverter()
        H = converter.convert(G)
        loader.dump(H, sys.argv[2])
    except Exception as ex:
        sys.stderr.write(ex)


if __name__ == "__main__":
    main()
