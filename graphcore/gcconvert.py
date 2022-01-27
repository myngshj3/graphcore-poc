

import networkx as nx
import yaml
import sys
import json
import traceback



# yaml's presettings for load/dump
def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

yaml.add_representer(dict, represent_odict)

def construct_odict(loader, node):
    return dict(loader.construct_pairs(node))

yaml.add_constructor('tag:yaml.org,2002:map', construct_odict)

class GCYamlLoader:

    def __init__(self):
        pass

    # read_file
    def load(self, filename) -> nx.DiGraph:
        try:
            with open(filename, "r") as f:
                G = yaml.load(f, Loader=yaml.Loader)
                if 'constraints' not in G.graph.keys():
                    G.graph['constraints'] = {}
                return G
        except Exception as ex:
            sys.stderr.write("file open failed. no infection to current graph.")

    def dump(self, G: nx.DiGraph, filename: str) -> None:
        try:
            if filename is None:
                sys.stderr.write("filename not specified")
            else:
                with open(filename,'w') as f:
                    yaml.dump(G, f)
        except Exception as ex:
            sys.stderr.write("dump failed")


class GCGraphLoader:

    def __init__(self):
        pass

    # read_file
    def load(self, filename) -> nx.DiGraph:
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                G = nx.node_link_graph(data)
                return G
        except Exception as ex:
            sys.stderr.write("file open failed. no infection to current graph.")
            raise ex

    def dump(self, G: nx.DiGraph, filename: str) -> None:
        try:
            if filename is None:
                sys.stderr.write("filename not specified")
            else:
                data = nx.node_link_data(G)
                with open(filename,'w') as f:
                    json.dump(data, f)
        except Exception as ex:
            sys.stderr.write("dump failed")
            raise ex

class GCConverter:

    def __init__(self):
        pass

    def convert(self, G, **args):
        try:
            data = nx.node_link_data(G)
            H = nx.node_link_graph(data)
            for n in H.nodes:
                for k in H.nodes[n].keys():
                    H.nodes[n][k] = H.nodes[n][k]['value']
            for e in H.edges:
                for k in H.edges[e[0], e[1]].keys():
                    H.edges[e[0], e[1]][k] = H.edges[e[0], e[1]][k]['value']
            if 'version' not in H.graph.keys():
                H.graph['version'] = "0.1.0"
            if 'micro_version' not in H.graph.keys():
                H.graph['micro-version'] = "20220123.1457"
            return H
        except Exception as ex:
            sys.stderr.write("convert error")
            raise ex


def main():
    try:
        if len(sys.argv) < 3:
            sys.stderr.write("file not specified")
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
