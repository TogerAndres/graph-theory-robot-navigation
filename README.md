Here is your text translated into English, keeping the technical tone and structure:

---

# NAVBOT — Intelligent Navigation System for Autonomous Robots

**Graph Theory · Optimization Algorithms**

Project for the Discrete Mathematics course. NAVBOT is an interactive tool where a map of nodes and connections (a graph) is built on a canvas, and a simulated robot computes and travels the optimal path between two points using different classic graph theory algorithms.

📊 [View project presentation](https://docs.google.com/presentation/d/1zP8lLd59PJpKUsa1zfWuXVM7qeBia5eWMp34HWJJHD4/edit?usp=sharing) (also included in this repository as `NAVBOT_presentacion.pptx`).

## Description

The goal of NAVBOT is to visually and practically demonstrate how graph algorithms are applied to the real-world problem of autonomous robot navigation within a map containing obstacles and paths with different costs.

The user builds their own map directly in the browser:

1. **Add nodes** (locations) by clicking on the canvas.
2. **Connect nodes** with edges, assigning weights (route cost — which can represent distance, time, energy, etc.).
3. **Block routes** to simulate obstacles; the system recalculates alternative paths.
4. **Select a source node and a destination node**.
5. **Run an algorithm** from the control panel; the robot animates the computed path in real time on the canvas.

All algorithm logic runs in the backend (Python + NetworkX), which receives the user-drawn graph as JSON, performs the computation, and returns the path, its cost, and step-by-step execution for educational purposes.

## Implemented Algorithms

| Algorithm                            | What it solves                                                   | Negative weights | Complexity                   |
| ------------------------------------ | ---------------------------------------------------------------- | ---------------- | ---------------------------- |
| **Dijkstra**                         | Shortest path from a source node                                 | ❌                | O((V+E) log V)               |
| **Bellman-Ford**                     | Shortest path, detects negative cycles                           | ✅                | O(V·E)                       |
| **Kruskal**                          | Minimum spanning tree (lowest-cost network connecting all nodes) | ✅                | O(E log E)                   |
| **TSP (Traveling Salesman Problem)** | Path that visits all nodes once and returns to the origin        | ✅                | O(n!) — limited to ≤10 nodes |
| **Connectivity analysis**            | Checks if the graph is connected, detects cycles and components  | —                | O(V+E)                       |

Each algorithm is exposed as an independent API endpoint and returns not only the final result but also a step-by-step trace (`steps`) shown in the interface for educational purposes — for example, in Dijkstra you can see each edge relaxation in the order it occurred.

### Why these algorithms?

* **Dijkstra** is the baseline case: fast and efficient, but only works with non-negative weights (it cannot represent “shortcuts” or bonuses).
* **Bellman-Ford** generalizes Dijkstra by allowing negative weights (for example, segments that represent energy savings or boosts) and also detects negative cycles (a design error in the map that would cause an infinite loop of cost improvement).
* **Kruskal** does not compute a path between two points, but rather the cheapest network connecting *all* nodes without cycles — useful for designing, for example, the minimum set of charging stations or sensors covering the entire map.
* **TSP** solves the problem of visiting multiple delivery or inspection points in the most efficient order while returning to the starting point. Since it grows factorially, the project limits it to graphs of up to 10 nodes to remain computationally feasible.

## Project Structure

```
navbot/
├── app.py                       # Flask backend + NetworkX: exposes algorithm APIs
├── templates/
│   └── index.html               # Frontend: interactive canvas, UI, and animation logic
├── NAVBOT_presentacion.pptx      # Project presentation (14 slides)
├── requirements.txt
└── README.md
```

## Technologies

**Backend**

* Python 3
* Flask + Flask-CORS
* NetworkX (graph algorithm implementation)

**Frontend**

* HTML, CSS, and vanilla JavaScript (no frameworks)
* Native browser canvas for drawing the graph and animating the robot

## Installation and Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
python app.py
```

### 3. Open in the browser

```
http://localhost:5000
```

> You can also open `templates/index.html` directly using a Live Server extension (port 5500); the API already accepts requests from both origins (see CORS configuration in `app.py`).

### Quick Demo

The **⚡ LOAD DEMO** button in the interface loads a preconfigured map with 6 nodes, ready to run any algorithm without manually drawing the graph.

## Mathematical Foundation

The map is modeled as a formal graph:

```
G = (V, E)
V = {A, B, C, D, ...}   ← nodes (map locations)
E = {(A,B,4), (B,C,2)}  ← weighted edges (route cost)
```

Depending on the algorithm, the graph is treated as directed (Dijkstra, Bellman-Ford) or undirected (Kruskal, TSP, connectivity analysis), reflecting whether routes allow one-way or bidirectional movement.

## Project Status

Fully functional academic project developed for the Discrete Mathematics course. It includes algorithm implementations, an interactive interface, and the final presentation.

## Author

Roger Andrés Álvarez Díaz — Discrete Mathematics Project.
