from __future__ import annotations

import networkx as nx


class WorkflowGraphBuilder:
    def build(self, graph_data: dict[str, dict[str, object]]) -> nx.DiGraph:
        graph = nx.DiGraph()

        for screen_id, data in graph_data.items():
            title = str(data.get("title", screen_id))
            graph.add_node(screen_id, title=title, depth=int(data.get("depth", 0)))

            options = data.get("options", [])
            for option in options if isinstance(options, list) else []:
                option_id = str(option).split(maxsplit=1)[0]
                edge_id = f"{screen_id}:{option_id}"
                graph.add_node(edge_id, option=str(option), kind="menu_option")
                graph.add_edge(screen_id, edge_id)

        return graph
