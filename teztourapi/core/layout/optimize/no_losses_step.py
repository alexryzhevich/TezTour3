from typing import List
import numpy as np
import pandas as pd

from core.layout.layout import Layout
from core.config import layout as layout_config
from core.layout.util import get_required_col, get_layout_col
from exceptions.exceptions import RESTRICTION_VIOLATION_ERROR_CODE
from exceptions.structs import ErrorMessage


def no_losses_step(layout: Layout, available_in_places, available_out_places, corrected_relations):
    _remove_in_losses(layout, available_in_places, corrected_relations)
    _remove_out_losses(layout, available_in_places, available_out_places, corrected_relations)


def _remove_in_losses(layout: Layout, available_in_places, corrected_relations):
    graph = _convert_to_in_graph(layout, available_in_places, corrected_relations)
    in_losses = _find_in_dates_to_remove_losses(layout, available_in_places)
    for v, losses in in_losses:
        _relax_vertex(layout, graph, v, losses)


def _remove_out_losses(layout: Layout, available_in_places, available_out_places, corrected_relations):
    graph = _convert_to_out_graph(layout, available_in_places, corrected_relations)
    out_losses = _find_out_dates_to_remove_losses(layout, available_out_places)
    for v, losses in out_losses:
        _relax_vertex(layout, graph, v, losses, True)


class Vertex(object):

    def __init__(self, row: int, no_losses: bool, date):
        self.row = row
        self.no_losses = no_losses
        self.date = date
        self.skip = False


class Edge(object):

    def __init__(self, from_v: int, to_v: int, row: int, from_places: int, to_places: int, from_pr: float, to_pr: float,
                 from_max_places, to_max_places):
        self.from_v = from_v
        self.to_v = to_v
        self.row = row
        self.from_places = from_places
        self.to_places = to_places
        self.from_pr = from_pr
        self.to_pr = to_pr
        self.from_max_places = from_max_places
        self.to_max_places = to_max_places


VertexList = List[Vertex]
EdgeList = List[Edge]
VertexEdgeList = List[EdgeList]


class Graph(object):

    def __init__(self, vertexes: VertexList, edges: VertexEdgeList, in_edges: VertexEdgeList):
        self.vertexes = vertexes
        self.edges = edges
        self.in_edges = in_edges


def _find_in_dates_to_remove_losses(layout: Layout, available_in_places):
    layout_data = layout.data
    height = layout_data.shape[0]
    width = layout.width
    losses = []
    cur_vertex_idx = 0
    for i in range(height):
        if pd.isnull(layout_data[layout_config.IN_PLACES_COL][i]):
            continue
        cur_sum = 0
        cur_idx = i % width
        for j in range(i, min(i + layout.max_days + 1, height)):
            delta = (layout_data[layout_config.OUT_DATES_COL][j] - layout_data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if not layout_data[get_required_col(cur_idx)][j] and not pd.isnull(layout_data[get_layout_col(cur_idx)][j]):
                cur_sum += int(layout_data[get_layout_col(cur_idx)][j])
        in_max_places = available_in_places[i]
        if in_max_places is not None and cur_sum > in_max_places:
            raise ErrorMessage(RESTRICTION_VIOLATION_ERROR_CODE,
                               'Sum of places is bigger than maximum of available {} in-places'.format(i))
        if in_max_places is not None and in_max_places - cur_sum > 0 and layout.no_losses[i][0]:
            losses.append((cur_vertex_idx, int(in_max_places - cur_sum)))
        cur_vertex_idx += 1
    return losses


def _find_out_dates_to_remove_losses(layout: Layout, available_out_places):
    layout_data = layout.data
    height = layout_data.shape[0]
    width = layout.width
    losses = []
    cur_vertex_idx = 0
    for i in range(height):
        if pd.isnull(layout_data[layout_config.OUT_PLACES_COL][i]):
            continue
        cur_sum = 0
        for j in range(width):
            cur_idx = get_layout_col(j)
            cur_req_idx = get_required_col(j)
            if pd.isnull(layout_data[cur_idx][i]) or layout_data[cur_req_idx][i]:
                continue
            cur_sum += int(layout_data[cur_idx][i])
        out_max_places = available_out_places[i]
        if out_max_places is not None and cur_sum > out_max_places:
            raise ErrorMessage(RESTRICTION_VIOLATION_ERROR_CODE,
                               'Sum of places is bigger than maximum of available {} out-places'.format(i))
        if out_max_places is not None and out_max_places - cur_sum > 0 and layout.no_losses[i][1]:
            losses.append((cur_vertex_idx, int(out_max_places - cur_sum)))
        cur_vertex_idx += 1
    return losses


def _convert_to_in_graph(layout: Layout, available_in_places, corrected_relations):
    # 0 -> no edge
    # required -> no edge
    height = layout.data.shape[0]
    layout_data = layout.data
    vertexes = []
    vertex_ids = [None for _ in range(height)]
    for i in range(height):
        if pd.isnull(layout_data[layout_config.IN_PLACES_COL][i]):
            continue
        vertex_ids[i] = len(vertexes)
        vertexes.append(Vertex(i, layout.no_losses[i][0], layout_data[layout_config.IN_DATES_COL][i]))
    edges = [[] for _ in range(len(vertexes))]
    in_edges = [[] for _ in range(len(vertexes))]
    for i in range(height):
        if vertex_ids[i] is None:
            continue
        cur_idx = i % layout.width
        for j in range(i, min(i + layout.max_days + 1, height)):
            delta = (layout_data[layout_config.OUT_DATES_COL][j] - layout_data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if layout_data[get_required_col(cur_idx)][j] or pd.isnull(layout_data[get_layout_col(cur_idx)][j]):
                continue
            from_relation = corrected_relations[i][delta - layout.min_days]
            for k in range(1, min(layout.width + 1, height - i)):
                delta2 = (layout_data[layout_config.OUT_DATES_COL][j] - layout_data[layout_config.IN_DATES_COL][i + k]).days
                if np.isnan(delta2) or vertex_ids[i + k] is None:
                    continue
                if delta2 < layout.min_days or delta2 > layout.max_days:
                    break
                to_relation = corrected_relations[i + k][delta2 - layout.min_days]
                cur_idx2 = (i + k) % layout.width
                if layout_data[get_required_col(cur_idx2)][j] or pd.isnull(layout_data[get_layout_col(cur_idx2)][j]):
                    continue
                edge = Edge(vertex_ids[i], vertex_ids[i + k], j, int(layout_data[get_layout_col(cur_idx)][j]),
                            int(layout_data[get_layout_col(cur_idx2)][j]), from_relation, to_relation,
                            available_in_places[i], available_in_places[i + k])
                edges[vertex_ids[i]].append(edge)
                in_edges[vertex_ids[i + k]].append(edge)

    return Graph(vertexes, edges, in_edges)


def _convert_to_out_graph(layout: Layout, available_in_places, corrected_relations):
    # 0 -> no edge
    # required -> no edge
    height = layout.data.shape[0]
    layout_data = layout.data
    vertexes = []
    vertex_ids = [None for _ in range(height)]
    for i in range(height):
        if pd.isnull(layout_data[layout_config.OUT_PLACES_COL][i]):
            continue
        vertex_ids[i] = len(vertexes)
        vertexes.append(Vertex(i, layout.no_losses[i][1], layout_data[layout_config.OUT_DATES_COL][i]))
    edges = [[] for _ in range(len(vertexes))]
    in_edges = [[] for _ in range(len(vertexes))]
    for i in range(height):
        if pd.isnull(layout_data[layout_config.IN_PLACES_COL][i]):
            continue
        cur_idx = i % layout.width
        for j in range(i, min(i + layout.max_days + 1, height)):
            if vertex_ids[j] is None:
                    continue
            delta = (layout_data[layout_config.OUT_DATES_COL][j] - layout_data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if layout_data[get_required_col(cur_idx)][j] or pd.isnull(layout_data[get_layout_col(cur_idx)][j]):
                continue
            from_relation = corrected_relations[i][delta - layout.min_days]
            for k in range(1, min(layout.width + 1, height - j)):
                delta2 = (layout_data[layout_config.OUT_DATES_COL][j + k] - layout_data[layout_config.IN_DATES_COL][i]).days
                if np.isnan(delta2) or vertex_ids[j + k] is None:
                    continue
                if delta2 < layout.min_days or delta2 > layout.max_days:
                    break
                to_relation = corrected_relations[i][delta2 - layout.min_days]
                if layout_data[get_required_col(cur_idx)][j + k] or pd.isnull(layout_data[get_layout_col(cur_idx)][j + k]):
                    continue
                edge = Edge(vertex_ids[j + k], vertex_ids[j], i, layout_data[get_layout_col(cur_idx)][j + k],
                            layout_data[get_layout_col(cur_idx)][j], from_relation, to_relation,
                            available_in_places[i], available_in_places[i])
                edges[vertex_ids[j + k]].append(edge)
                in_edges[vertex_ids[j]].append(edge)

    return Graph(vertexes, edges, in_edges)


def _relax_vertex(layout: Layout, graph: Graph, v: int, losses: int, out: bool=False):
    new_values = {i: {} for i in range(layout.width)}
    while losses > 0:
        path = _find_path_from_vertex(graph, v)
        if path is None:
            if _count_skipped_vertexes(graph) > 0:
                _remove_skip_indicators(graph)
                continue
            break  # TODO throw cannot remove losses
        _relax_by_path(graph, path)
        if out:
            _update_out_new_values(layout, graph, path, new_values)
        else:
            _update_in_new_values(layout, graph, path, new_values)
        _shuffle_edges(graph)
        losses -= 1
    _update_layout(layout, new_values)


def _find_path_from_vertex(graph: Graph, v: int):
    v_path = [v]
    e_path = [None]
    next_e = [0] * len(graph.vertexes)
    while len(v_path) > 0:
        cur_v = v_path[-1]
        if not graph.vertexes[cur_v].no_losses and not graph.vertexes[cur_v].skip:
            break
        if next_e[cur_v] == len(graph.edges[cur_v]):
            v_path.pop()
            e_path.pop()
            continue
        next_edge = graph.edges[cur_v][next_e[cur_v]]
        if next_edge.to_places > 0:
            e_path.append(next_edge)
            v_path.append(next_edge.to_v)
        next_e[cur_v] += 1
    path = e_path[1:]
    return None if len(path) == 0 else path


def _relax_by_path(graph: Graph, path: EdgeList):
    graph.vertexes[path[-1].to_v].skip = True
    for edge in path:
        for out_edge in graph.edges[edge.from_v]:
            if out_edge.row != edge.row:
                continue
            out_edge.from_places += 1
        for in_edge in graph.in_edges[edge.from_v]:
            if in_edge.row != edge.row:
                continue
            in_edge.to_places += 1
        for in_edge in graph.in_edges[edge.to_v]:
            if in_edge.row != edge.row:
                continue
            in_edge.to_places -= 1
        for out_edge in graph.edges[edge.to_v]:
            if out_edge.row != edge.row:
                continue
            out_edge.from_places -= 1


def _update_in_new_values(layout: Layout, graph: Graph, path: EdgeList, new_values):
    for edge in path:
        if edge.row not in new_values[graph.vertexes[edge.from_v].row % layout.width]:
            new_values[graph.vertexes[edge.from_v].row % layout.width][edge.row] = int(layout.data[get_layout_col(graph.vertexes[edge.from_v].row % layout.width)][edge.row])
        if edge.row not in new_values[graph.vertexes[edge.to_v].row % layout.width]:
            new_values[graph.vertexes[edge.to_v].row % layout.width][edge.row] = int(layout.data[get_layout_col(graph.vertexes[edge.to_v].row % layout.width)][edge.row])
        new_values[graph.vertexes[edge.from_v].row % layout.width][edge.row] += 1
        new_values[graph.vertexes[edge.to_v].row % layout.width][edge.row] -= 1


def _update_out_new_values(layout: Layout, graph: Graph, path: EdgeList, new_values):
    for edge in path:
        if graph.vertexes[edge.from_v].row not in new_values[edge.row % layout.width]:
            new_values[edge.row % layout.width][graph.vertexes[edge.from_v].row] = int(layout.data[get_layout_col(edge.row % layout.width)][graph.vertexes[edge.from_v].row])
        if graph.vertexes[edge.to_v].row not in new_values[edge.row % layout.width]:
            new_values[edge.row % layout.width][graph.vertexes[edge.to_v].row] = int(layout.data[get_layout_col(edge.row % layout.width)][graph.vertexes[edge.to_v].row])
        new_values[edge.row % layout.width][graph.vertexes[edge.from_v].row] += 1
        new_values[edge.row % layout.width][graph.vertexes[edge.to_v].row] -= 1


def _shuffle_edges(graph: Graph):
    for edges in graph.edges:
        weighted_shuffle(edges)


def weighted_shuffle(edges: EdgeList):
    if len(edges) == 0:
        return
    # w = [(e.from_pr * (e.to_places / graph.vertexes[e.to_v].places)) /
    #      ((e.from_places / graph.vertexes[e.from_v].places) * e.to_pr) if e.from_places * e.to_pr > 0 else 10. for e in edges]
    w = _get_edges_weights(edges)
    indexes = list(range(len(w)))
    indexes.sort(key=w.__getitem__)
    sorted_edges = map(edges.__getitem__, indexes[::-1])
    edges[:] = sorted_edges


def _get_edges_weights(edges: EdgeList):
    return [_get_edge_weight(e) for e in edges]


def _get_edge_weight(edge: Edge):
    if edge.to_max_places == 0:
        return 0
    if edge.from_max_places == 0:
        return 10.
    return min(edge.from_pr / (edge.from_places / edge.from_max_places), (edge.to_places / edge.to_max_places) / edge.to_pr)
    # if (edge.to_places / edge.to_max_places) > edge.to_pr:
    #     return edge.from_pr / (edge.from_places / edge.from_max_places)
    # return (edge.to_places / edge.to_max_places) / edge.to_pr


def _remove_skip_indicators(graph: Graph):
    for vertex in graph.vertexes:
        vertex.skip = False


def _count_skipped_vertexes(graph: Graph):
    count = 0
    for vertex in graph.vertexes:
        count += int(vertex.skip)
    return count


def _update_layout(layout: Layout, new_values: dict):
    for i, vals in new_values.items():
        layout.data[get_layout_col(i)][list(vals.keys())] = list(vals.values())
