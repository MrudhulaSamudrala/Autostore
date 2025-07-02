import heapq

def astar(start, goal, neighbors_fn, heuristic_fn):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic_fn(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        for neighbor in neighbors_fn(current):
            tentative_g_score = g_score[current] + 1  # Assume cost=1 for all moves
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic_fn(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_grid(start, goal, obstacles, grid_size=None):
    """
    A* pathfinding for a 2D grid warehouse.
    start: (x, y)
    goal: (x, y)
    obstacles: set of (x, y) tuples
    grid_size: (width, height) or None for unlimited
    Returns: list of (x, y) from start to goal, or None if no path
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan(start, goal)}
    closed_set = set()

    def neighbors(pos):
        x, y = pos
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if grid_size:
                if not (0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]):
                    continue
            if (nx, ny) in obstacles:
                continue
            yield (nx, ny)

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        closed_set.add(current)
        for neighbor in neighbors(current):
            if neighbor in closed_set:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + manhattan(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None 