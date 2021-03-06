"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"

Edited by Tom and Irit Inbar
This will be the UI model to get data from the data model and display it
"""
import sys
from types import SimpleNamespace

from client import Client
import json
from pygame import gfxdraw
import pygame
from pygame import *
import networkx as nx
import Algo as al
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

graph_json = client.get_graph()

FONT = pygame.font.SysFont('Arial', 20, bold=True)
# load the json string into SimpleNamespace Object

graph = json.loads(
    graph_json, object_hook=lambda json_dict: SimpleNamespace(**json_dict))

for n in graph.Nodes:
    x, y, _ = n.pos.split(',')
    n.pos = SimpleNamespace(x=float(x), y=float(y))

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


G = nx.DiGraph()

# Convert from json to networkX graph
for n in graph.Nodes:
    x = n.pos.x
    y = n.pos.y
    G.add_node(n.id, pos=(my_scale(float(x), x=True), my_scale(float(y), y=True)))

for e in graph.Edges:
    G.add_edge(e.src, e.dest, weight=e.w)

myAlgo = al.Algo(G)
myAlgo.change = True
radius = 15

info = client.get_info()
info_json = json.loads(info)

for i in range(info_json['GameServer']['agents']):
    place = "{\"id\":" + str(0) + "}"
    client.add_agent(place)

# this commnad starts the server - the game is running now
client.start()

# This info will be used to display 'Catch!' for 60 frames after a pokemon is caught
current_pokemons = 0

current_grade = 0
catch_timer = 0
catch_pos = [0, 0]

while client.is_running() == 'true':

    # Get agents and pokemons data from client
    pokemons = json.loads(client.get_pokemons(),
                          object_hook=lambda d: SimpleNamespace(**d)).Pokemons
    pokemons = [p.Pokemon for p in pokemons]
    for p in pokemons:
        x, y, _ = p.pos.split(',')
        p.pos = SimpleNamespace(x=my_scale(
            float(x), x=True), y=my_scale(float(y), y=True))

    # Sort pokemon list by value
    # Most valuable pokemons will be at the head of the list
    pokemons.sort(key=lambda x: x.value, reverse=False)

    agents = json.loads(client.get_agents(),
                        object_hook=lambda d: SimpleNamespace(**d)).Agents
    agents = [agent.Agent for agent in agents]

    # Sort agent list by speed
    # Fastest agents will be at the head of the list
    agents.sort(key=lambda x: x.speed, reverse=False)

    for a in agents:
        x, y, _ = a.pos.split(',')
        a.pos = SimpleNamespace(x=my_scale(
            float(x), x=True), y=my_scale(float(y), y=True))

    # check events
    # If Q is pressed or exit button then quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit()
            exit(0)
            client.stop_connection()
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(pygame.mouse.get_pos())

    # refresh surface
    screen.fill(Color(10, 10, 10))

    # Get current state info
    info = client.get_info()
    info_json = json.loads(info)

    # Check if the grade changed, that means we caught a pokemon
    if info_json['GameServer']['grade'] > current_grade:
        current_grade = info_json['GameServer']['grade']
        catch_timer = 60
        catch_pos = [int(agents[0].pos.x), int(agents[0].pos.y)]
        myAlgo.change = True

    # Check if current pokemon number is larger than previous -> need to calculate new path
    if info_json['GameServer']['pokemons'] > current_pokemons:
        myAlgo.notify_change(pokemons)

    current_pokemons = info_json['GameServer']['pokemons']

    # draw current game information
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
        # src_x = my_scale(G.node.get(src)['pos'][0], x=True)
        # src_y = my_scale(G.node.get(src)['pos'][1], y=True)
        # dest_x = my_scale(G.node.get(dest)['pos'][0], x=True)
        # dest_y = my_scale(G.node.get(dest)['pos'][1], y=True)

        src_x = G.node.get(src)['pos'][0]
        src_y = G.node.get(src)['pos'][1]
        dest_x = G.node.get(dest)['pos'][0]
        dest_y = G.node.get(dest)['pos'][1]

        # draw line between nodes
        pygame.draw.line(screen, Color(170, 170, 255),
                         (src_x, src_y), (dest_x, dest_y))

    # draw nodes
    for n in G.nodes.items():
        x = n[1]['pos'][0]
        y = n[1]['pos'][1]
        n_id = str(n[0])

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

    # draw digimons based on their type \ which way they are going
    for p in pokemons:
        if p.type == -1:
            # Cyan
            pygame.draw.circle(screen, Color(0, 255, 255), (int(p.pos.x), int(p.pos.y)), 10)
        else:
            # Purple / Magenta
            pygame.draw.circle(screen, Color(255, 0, 255), (int(p.pos.x), int(p.pos.y)), 10)

    if catch_timer > 0:
        catch_timer -= 1
        catch_text = FONT.render('Catch!', True, Color(255 - 240 + catch_timer * 4, 255 - 240 + catch_timer * 4,
                                                       255 - 240 + catch_timer * 4))
        catch_rect = catch_text.get_rect(center=(catch_pos[0], catch_pos[1] + 20 - catch_timer / 3))
        screen.blit(catch_text, catch_rect)

    # update screen changes
    display.update()

    # choose next edge
    myAlgo.choose(agents=agents, client=client, G=graph, pokemons=pokemons)

    client.move()

    # refresh rate
    clock.tick(10)
# game over:
