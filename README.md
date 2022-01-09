# Ex4_OOP
This project aims to simulate graph traversal.
Each simulation plays for about 30 to 60 seconds, and for each simulation a constant amount of 'agents' can travel the graph and if they pass through an edge with certain 'pokemon' they absorb him, adding his value to the current grade. The goal is to reach the end with a high grade.

## How to run
Open one terminal to run the server: <br>
Go to directory with java server and type
```
java -jar Ex4_server_v0.0.jar [number from 0 to 15]
```
Open another terminal to run the client:<br>
Go to the directory with python code and type 
```
python3 student_code.py
```
A window with simple GUI should then appear and simulate the game, while the terminal prints the current path of the agent if there is just one.

![DEMO](https://github.com/bfwontcodewithme/Ex4_OOP/blob/main/visual_info/how_it_works.png)

## Algorithm implementations
| Algorithm | Description |
| --- | --- |
| Graph database | With json from server, we construct a graph with the networkx library. |
| Algorithm | Using the networkx library, we calculate an approximation of the optimal route to help us capture as much pokemons as we can. |
| GUI | With pygame, and the code given to us, we improve upon the GUI by adding timer, setting 'q' as an exit button and displaying more useful information. |
