"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"

Edited by Tom and Irit Inbar
"""
import sys
from types import SimpleNamespace

import networkx

from client import Client
import json
from pygame import gfxdraw
import pygame
from pygame import *
import networkx as nx
import Algo

# init pygame
WIDTH, HEIGHT = 1080, 720

# default port
PORT = 6666
# server host (default localhost 127.0.0.1)
HOST = '127.0.0.1'
pygame.init()

screen = display.set_mode((WIDTH, HEIGHT), depth=32, flags=RESIZABLE)
clock = pygame.time.Clock()
pygame.font.init()

client = Client()
client.start_connection(HOST, PORT)

pokemons = client.get_pokemons()
pokemons_obj = json.loads(pokemons, object_hook=lambda d: SimpleNamespace(**d))

print(pokemons)

graph_json = client.get_graph()

FONT = pygame.font.SysFont('Arial', 20, bold=True)
# load the json string into SimpleNamespace Object

graph = json.loads(
    graph_json, object_hook=lambda json_dict: SimpleNamespace(**json_dict))

G = nx.DiGraph()

# Convert from json to networkX graph
for n in graph.Nodes:
    x, y, _ = n.pos.split(',')
    n.pos = SimpleNamespace(x=float(x), y=float(y))
    G.add_node(n.id, pos=(float(x), float(y)))

for e in graph.Edges:
    G.add_edge(e.src, e.dest, weight=e.w)

print(G)
# sys.exit(0)

# get data proportions
min_x = min(list(graph.Nodes), key=lambda n: n.pos.x).pos.x
min_y = min(list(graph.Nodes), key=lambda n: n.pos.y).pos.y
max_x = max(list(graph.Nodes), key=lambda n: n.pos.x).pos.x
max_y = max(list(graph.Nodes), key=lambda n: n.pos.y).pos.y


def scale(data, min_screen, max_screen, min_data, max_data):
    """
    get the scaled data with proportions min_data, max_data
    relative to min and max screen dimentions
    """
    return ((data - min_data) / (max_data - min_data)) * (max_screen - min_screen) + min_screen


# decorate scale with the correct values

def my_scale(data, x=False, y=False):
    if x:
        return scale(data, 50, screen.get_width() - 50, min_x, max_x)
    if y:
        return scale(data, 50, screen.get_height() - 50, min_y, max_y)


radius = 15

client.add_agent("{\"id\":0}")
# client.add_agent("{\"id\":1}")
# client.add_agent("{\"id\":2}")
# client.add_agent("{\"id\":3}")

# this commnad starts the server - the game is running now
client.start()

"""
The code below should be improved significantly:
The GUI and the "algo" are mixed - refactoring using MVC design pattern is required.
"""

while client.is_running() == 'true':

    pokemons = json.loads(client.get_pokemons(),
                          object_hook=lambda d: SimpleNamespace(**d)).Pokemons
    pokemons = [p.Pokemon for p in pokemons]
    for p in pokemons:
        x, y, _ = p.pos.split(',')
        p.pos = SimpleNamespace(x=my_scale(
            float(x), x=True), y=my_scale(float(y), y=True))

    agents = json.loads(client.get_agents(),
                        object_hook=lambda d: SimpleNamespace(**d)).Agents
    agents = [agent.Agent for agent in agents]

    for a in agents:
        x, y, _ = a.pos.split(',')
        a.pos = SimpleNamespace(x=my_scale(
            float(x), x=True), y=my_scale(float(y), y=True))

    # check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit()
            exit(0)
            client.stop_connection()

    # refresh surface
    screen.fill(Color(0, 0, 0))

    info = client.get_info()
    info_json = json.loads(info)

    # draw information
    x = screen.get_width() * 0.08
    y = screen.get_height() * 0.025
    text_info = FONT.render('press q to quit', True, Color(255, 255, 255))
    text_rect = text_info.get_rect(center=(x, y))
    screen.blit(text_info, text_rect)

    y = screen.get_height() * 0.055
    text_info = FONT.render('Points:' + str(info_json['GameServer']['grade']), True, Color(255, 255, 255))
    text_rect = text_info.get_rect(center=(x, y))
    screen.blit(text_info, text_rect)

    y = screen.get_height() * 0.085
    text_info = FONT.render('Moves made:' + str(info_json['GameServer']['moves']), True, Color(255, 255, 255))
    text_rect = text_info.get_rect(center=(x, y))
    screen.blit(text_info, text_rect)

    y = screen.get_height() * 0.115
    text_info = FONT.render('Time left(s):' + str(int(client.time_to_end()) / 1000), True, Color(255, 255, 255))
    text_rect = text_info.get_rect(center=(x, y))
    screen.blit(text_info, text_rect)

    # draw edges
    for e in G.edges.items():
        src = e[0][0]
        dest = e[0][1]
        weight = e[1]['weight']

        # scaled positions
        src_x = my_scale(G.node.get(src)['pos'][0], x=True)
        src_y = my_scale(G.node.get(src)['pos'][1], y=True)
        dest_x = my_scale(G.node.get(dest)['pos'][0], x=True)
        dest_y = my_scale(G.node.get(dest)['pos'][1], y=True)

        # draw the line
        pygame.draw.line(screen, Color(170, 170, 255),
                         (src_x, src_y), (dest_x, dest_y))

    # draw nodes
    for n in G.nodes.items():
        n_x = n[1]['pos'][0]
        n_y = n[1]['pos'][1]
        n_id = str(n[0])

        x = my_scale(n_x, x=True)
        y = my_scale(n_y, y=True)

        # its just to get a nice antialiased circle
        gfxdraw.filled_circle(screen, int(x), int(y),
                              radius, Color(64, 80, 174))
        gfxdraw.aacircle(screen, int(x), int(y),
                         radius, Color(255, 255, 255))

        # draw the node id
        id_srf = FONT.render(n_id, True, Color(255, 255, 255))
        rect = id_srf.get_rect(center=(x, y))
        screen.blit(id_srf, rect)

    # draw agents
    for agent in agents:
        pygame.draw.circle(screen, Color(122, 61, 23),
                           (int(agent.pos.x), int(agent.pos.y)), 10)
    # draw pokemons (note: should differ (GUI wise) between the up and the down pokemons (currently they are marked in the same way).
    for p in pokemons:
        pygame.draw.circle(screen, Color(0, 255, 255), (int(p.pos.x), int(p.pos.y)), 10)

    # update screen changes
    display.update()

    # refresh rate
    clock.tick(60)

    # choose next edge
    Algo.choose(agents=agents, client=client, G=graph)

    client.move()
# game over:
