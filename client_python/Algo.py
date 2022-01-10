import networkx as nx

"""
This data model will receive data from the server, process it and forward it to the UI model.
The data received will be the current pokemons and their locations, and the current agents.
"""


class Algo:
    EPSILON = 0.00001

    def __init__(self, DiGraph: nx.DiGraph):
        self.DG = DiGraph
        self.CEN = nx.center(self.DG)[0]
        self.path = []
        self.change = False

    def choose(self, agents, client, G, pokemons):
        if len(agents) == 1:
            return self.single_choose(agents, client,pokemons)

        else:
            alen = len(agents)
            self.path = [[] for _ in range(alen)]
            plen = len(pokemons)

            if alen == 0 or plen == 0:
                return

            z = 0
            for a in agents:

                path = [a.src] + list(self.find_nodes(pokemon=pokemons[z]))
                self.path[z] = nx.algorithms.approximation.traveling_salesman_problem(G=self.DG, nodes=path, cycle=True)

                if len(self.path[z]) > 0 and a.dest == -1:
                    client.choose_next_edge(
                        '{"agent_id":' + str(a.id) + ', "next_node_id":' + str(self.path[z].pop(1)) + '}')

                z += 1
                if z == plen:
                    break

        # else:
        #     for agent in agents:
        #         if agent.dest == -1:
        #             next_node = (agent.src - 1) % len(G.Nodes)
        #             client.choose_next_edge(
        #                 '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(next_node) + '}')
        #             ttl = client.time_to_end()
        #             print(ttl, client.get_info())

    def single_choose(self, agents, client, pokemons):

        if self.change:
            self.path.clear()
            path = [agents[0].src]
            # self.path = [agents[0].src]
            for p in pokemons:

                between_these = self.find_nodes(p)
                path += [between_these[1], between_these[0], between_these[1]]

                # self.path += nx.shortest_path(G=self.DG, source=agents[0].src, target=between_these[0])
                # self.path += nx.shortest_path(G=self.DG, source=between_these[0], target=between_these[1])
                # self.path += nx.shortest_path(G=self.DG, source=between_these[1], target=between_these[0])

            self.path = nx.algorithms.approximation.traveling_salesman_problem(G=self.DG, nodes=path, cycle=False, weight='Weight')

        # Path as in path to reach pokemon, if it is not empty
        if len(self.path) > 0 and agents[0].dest == -1:
            client.choose_next_edge(
                '{"agent_id":' + str(agents[0].id) + ', "next_node_id":' + str(self.path.pop(0)) + '}')

        elif len(self.path) == 0 and len(pokemons) > 0:
            self.path = nx.approximation.traveling_salesman_problem(G=self.DG, nodes=[agents[0].src] + list(self.find_nodes(pokemons[0])), cycle=False)

        self.change = False
        print(self.path)

    def notify_change(self, pokemons):
        self.change = True

    def find_nodes(self, pokemon):

        px = pokemon.pos.x
        py = pokemon.pos.y

        for n1 in self.DG.nodes.items():
            for n2 in self.DG.nodes.items():
                n1x, n1y = n1[1]['pos'][0], n1[1]['pos'][1]
                n1id = n1[0]

                n2x, n2y = n2[1]['pos'][0], n2[1]['pos'][1]
                n2id = n2[0]

                if n1id == n2id:
                    continue

                n1n2dist = self.dist(x1=n1x, y1=n1y, x2=n2x,y2= n2y)
                pdist = self.dist(x1=n1x, y1=n1y, x2= px, y2=py) + self.dist(x1=n2x, y1=n2y, x2=px, y2=py)

                if abs(n1n2dist - pdist) < self.EPSILON:
                    return n1id, n2id

    def dist(self, x1, y1, x2, y2):
        dt = (x2 - x1)**2 + (y2 - y1)**2
        dt = dt**0.5
        return dt

