import random

import networkx as nx
"""
This data model will receive data from the server, process it and forward it to the UI model.
"""


class Algo:
    EPSILON = 0.0000001

    def __init__(self, DiGraph):
        self.DG = DiGraph
        self.CEN = nx.center(self.DG)[0]
        self.path = []

    def choose(self, agents, client, G, pokemons):
        if len(agents) == 1:
            return self.single_choose(agents, client, G, pokemons)
        else:
            for agent in agents:
                if agent.dest == -1:
                    next_node = (agent.src - 1) % len(G.Nodes)
                    client.choose_next_edge(
                        '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(next_node) + '}')
                    ttl = client.time_to_end()
                    print(ttl, client.get_info())

    def single_choose(self, agents, client, G, pokemons):
        # Path as in path to reach pokemon, if it is not empty
        if not self.path:
            client.choose_next_edge(
                    '{"agent_id":' + str(0) + ', "next_node_id":' + str((agents[0].src - 1) % len(G.Nodes)) + '}')
#str(self.path.pop(0))
    def notify_change(self, pokemons):
        pass
        # pmons = []
        # for p in pokemons:
        #     pass
        # path = nx.algorithms.approximation.traveling_salesman_problem(self.DG, nodes= pmons,cycle=False)
        # print(path)

