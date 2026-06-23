from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import networkx as nx
import json
import math
from itertools import permutations

app = Flask(__name__)

# Permite requests desde Live Server (puerto 5500) y localhost
CORS(app, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5000",
    "null"  # Para abrir el HTML directo desde el sistema de archivos
])

# ─── HELPERS ────────────────────────────────────────────────

def build_graph(nodes, edges, directed=True):
    G = nx.DiGraph() if directed else nx.Graph()
    for n in nodes:
        G.add_node(n["id"], label=n.get("label", n["id"]))
    for e in edges:
        if not e.get("blocked", False):
            G.add_edge(e["source"], e["target"], weight=float(e.get("weight", 1)))
    return G


def path_cost(G, path):
    cost = 0
    for i in range(len(path) - 1):
        cost += G[path[i]][path[i+1]]["weight"]
    return round(cost, 4)


# ─── ROUTES ─────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dijkstra", methods=["POST"])
def dijkstra():
    data = request.json
    nodes = data["nodes"]
    edges = data["edges"]
    source = data["source"]
    target = data["target"]

    if not source or not target:
        return jsonify({"error": "Debes seleccionar nodo origen y destino."}), 400

    G = build_graph(nodes, edges, directed=True)

    try:
        path = nx.dijkstra_path(G, source, target, weight="weight")
        cost = path_cost(G, path)
        all_dist = dict(nx.single_source_dijkstra_path_length(G, source, weight="weight"))
        all_dist = {k: round(v, 4) for k, v in all_dist.items()}

        return jsonify({
            "algorithm": "Dijkstra",
            "path": path,
            "cost": cost,
            "all_distances": all_dist,
            "steps": build_dijkstra_steps(G, source, target)
        })
    except nx.NetworkXNoPath:
        return jsonify({"error": "No hay camino disponible entre los nodos seleccionados."}), 400
    except nx.NodeNotFound as e:
        return jsonify({"error": f"Nodo no encontrado: {str(e)}"}), 400


@app.route("/api/bellman_ford", methods=["POST"])
def bellman_ford():
    data = request.json
    nodes = data["nodes"]
    edges = data["edges"]
    source = data["source"]
    target = data["target"]

    if not source or not target:
        return jsonify({"error": "Debes seleccionar nodo origen y destino."}), 400

    G = build_graph(nodes, edges, directed=True)

    try:
        length, path = nx.single_source_bellman_ford(G, source, target=target, weight="weight")
        cost = round(length, 4)

        has_neg_cycle = False
        try:
            nx.find_negative_cycle(G, source)
            has_neg_cycle = True
        except nx.NetworkXError:
            pass

        return jsonify({
            "algorithm": "Bellman-Ford",
            "path": path,
            "cost": cost,
            "has_negative_cycle": has_neg_cycle,
            "steps": build_bf_steps(G, source)
        })
    except nx.NetworkXNoPath:
        return jsonify({"error": "No hay camino disponible entre los nodos seleccionados."}), 400
    except nx.NodeNotFound as e:
        return jsonify({"error": f"Nodo no encontrado: {str(e)}"}), 400


@app.route("/api/kruskal", methods=["POST"])
def kruskal():
    data = request.json
    nodes = data["nodes"]
    edges = data["edges"]

    G = build_graph(nodes, edges, directed=False)

    if not nx.is_connected(G):
        return jsonify({"error": "El grafo no está completamente conectado. Kruskal requiere grafo conexo."}), 400

    try:
        mst = nx.minimum_spanning_tree(G, algorithm="kruskal", weight="weight")
        mst_edges = [
            {"source": u, "target": v, "weight": round(d["weight"], 4)}
            for u, v, d in mst.edges(data=True)
        ]
        total_cost = round(sum(d["weight"] for _, _, d in mst.edges(data=True)), 4)

        return jsonify({
            "algorithm": "Kruskal (Árbol de Expansión Mínima)",
            "mst_edges": mst_edges,
            "total_cost": total_cost,
            "nodes_connected": list(mst.nodes())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tsp", methods=["POST"])
def tsp():
    data = request.json
    nodes = data["nodes"]
    edges = data["edges"]

    G = build_graph(nodes, edges, directed=False)
    node_ids = [n["id"] for n in nodes]

    if len(node_ids) > 10:
        return jsonify({"error": "TSP exacto solo disponible para ≤10 nodos (O(n!) es muy costoso)."}), 400

    if not nx.is_connected(G):
        return jsonify({"error": "El grafo no está completamente conectado para TSP."}), 400

    best_path = None
    best_cost = float("inf")
    start = node_ids[0]
    others = node_ids[1:]

    for perm in permutations(others):
        route = [start] + list(perm) + [start]
        try:
            cost = 0
            for i in range(len(route) - 1):
                cost += nx.shortest_path_length(G, route[i], route[i+1], weight="weight")
            if cost < best_cost:
                best_cost = cost
                best_path = route
        except nx.NetworkXNoPath:
            continue

    if best_path is None:
        return jsonify({"error": "No se encontró ruta TSP válida."}), 400

    return jsonify({
        "algorithm": "Problema del Agente Viajero (TSP)",
        "path": best_path,
        "cost": round(best_cost, 4),
        "nodes_visited": len(node_ids)
    })


@app.route("/api/connectivity", methods=["POST"])
def connectivity():
    data = request.json
    nodes = data["nodes"]
    edges = data["edges"]

    G_dir = build_graph(nodes, edges, directed=True)

    components = list(nx.weakly_connected_components(G_dir))
    is_connected = nx.is_weakly_connected(G_dir)

    return jsonify({
        "is_connected": is_connected,
        "components": [list(c) for c in components],
        "num_components": len(components),
        "node_count": G_dir.number_of_nodes(),
        "edge_count": G_dir.number_of_edges(),
        "has_cycles": not nx.is_directed_acyclic_graph(G_dir)
    })


@app.route("/api/compare", methods=["POST"])
def compare():
    data = request.json
    nodes = data["nodes"]
    edges = data["edges"]
    source = data["source"]
    target = data["target"]

    if not source or not target:
        return jsonify({"error": "Debes seleccionar nodo origen y destino para comparar."}), 400

    G = build_graph(nodes, edges, directed=True)
    result = {"source": source, "target": target}

    try:
        d_path = nx.dijkstra_path(G, source, target, weight="weight")
        d_cost = path_cost(G, d_path)
        result["dijkstra"] = {"path": d_path, "cost": d_cost}
    except Exception as e:
        result["dijkstra"] = {"error": str(e)}

    try:
        bf_len, bf_path = nx.single_source_bellman_ford(G, source, target=target, weight="weight")
        result["bellman_ford"] = {"path": bf_path, "cost": round(bf_len, 4)}
    except Exception as e:
        result["bellman_ford"] = {"error": str(e)}

    return jsonify(result)


# ─── STEP BUILDERS ────────────────────────────────────────

def build_dijkstra_steps(G, source, target):
    steps = []
    dist = {n: float("inf") for n in G.nodes()}
    dist[source] = 0
    visited = set()

    steps.append({
        "action": "Inicializar",
        "description": f"Distancia a '{source}' = 0. Todos los demás = ∞"
    })

    import heapq
    heap = [(0, source)]

    while heap:
        current_dist, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)

        for v, data in G[u].items():
            w = data["weight"]
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
                steps.append({
                    "action": "Relajar arista",
                    "description": f"Ruta {u}→{v}: {round(dist[u],2)} + {w} = {round(new_dist,2)} (actualizado)"
                })

        if u == target:
            break

    return steps[:20]


def build_bf_steps(G, source):
    steps = []
    dist = {n: float("inf") for n in G.nodes()}
    dist[source] = 0

    steps.append({
        "action": "Inicializar",
        "description": f"Distancia a '{source}' = 0. Todos los demás = ∞",
        "iteration": 0
    })

    nodes = list(G.nodes())
    for i in range(len(nodes) - 1):
        updated = False
        for u, v, data in G.edges(data=True):
            w = data["weight"]
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
                if len(steps) < 20:
                    steps.append({
                        "action": f"Iteración {i+1}",
                        "description": f"Relaja {u}→{v}: nueva distancia = {round(dist[v],2)}",
                        "iteration": i + 1
                    })
        if not updated:
            steps.append({
                "action": "Convergencia",
                "description": f"Sin cambios en iteración {i+1}. Algoritmo terminado.",
                "iteration": i+1
            })
            break

    return steps


if __name__ == "__main__":
    app.run(debug=True, port=5000)