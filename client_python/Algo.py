def choose(agents, client, G):
    for agent in agents:
        if agent.dest == -1:
            next_node = (agent.src - 1) % len(G.Nodes)
            client.choose_next_edge(
                '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(next_node) + '}')
            ttl = client.time_to_end()
            print(ttl, client.get_info())