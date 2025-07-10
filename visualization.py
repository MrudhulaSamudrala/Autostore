import random as pyrandom
import heapq
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from vpython import *
import time

spacing = 1.2  # or whatever value you want for the space between cubes

# --- Data Classes ---
class Bin:
    def __init__(self, bin_id, product_id=None):
        self.id = bin_id
        self.product_id = product_id
        self.color = (pyrandom.random(), pyrandom.random(), pyrandom.random())

class BinStack:
    def __init__(self, max_height=5):
        self.bins = []
        self.max_height = max_height

    def add_bin(self, bin_item):
        if len(self.bins) < self.max_height:
            self.bins.append(bin_item)
            return True
        return False

    def get_top_bin(self):
        return self.bins[-1] if self.bins else None

    def remove_top_bin(self):
        return self.bins.pop() if self.bins else None

    @property
    def current_height(self):
        return len(self.bins)

class Grid:
    def __init__(self, width, depth, stack_height=5):
        self.width = width
        self.depth = depth
        self.stack_height = stack_height
        self.grid = [
            [BinStack(max_height=stack_height) for _ in range(depth)]
            for _ in range(width)
        ]
        bin_counter = 1
        for x in range(width):
            for y in range(depth):
                # Fill every stack to the same height
                for _ in range(stack_height):
                    product = f"P{bin_counter}"
                    new_bin = Bin(f"B{bin_counter}", product_id=product)
                    self.grid[x][y].add_bin(new_bin)
                    bin_counter += 1

    def get_stack(self, x, y):
        return self.grid[x][y]

# --- Pathfinding ---
def astar_2d_then_down(start, goal, grid):
    width, depth = grid.width, grid.depth

    def neighbors_2d(node):
        x, y = node
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < depth:
                if grid.get_stack(nx, ny).current_height > 0:
                    yield (nx, ny)

    def heuristic_2d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0 + heuristic_2d(start[:2], goal[:2]), 0, start[:2], [start]))

    visited = set()

    while open_set:
        _, cost, current, path = heapq.heappop(open_set)

        if current == goal[:2]:
            down_path = []
            cx, cy = current
            current_stack = grid.get_stack(cx, cy)
            top_z = current_stack.current_height - 1

            for z in reversed(range(goal[2] + 1, top_z + 1)):
                down_path.append((cx, cy, z))

            down_path.append(goal)
            return path + down_path

        if current in visited:
            continue
        visited.add(current)

        for neighbor in neighbors_2d(current):
            if neighbor not in visited:
                stack = grid.get_stack(neighbor[0], neighbor[1])
                top_z = stack.current_height - 1
                heapq.heappush(open_set, (
                    cost + 1 + heuristic_2d(neighbor, goal[:2]),
                    cost + 1,
                    neighbor,
                    path + [(neighbor[0], neighbor[1], top_z)]
                ))
    return None

# --- Visualization ---
def visualize_grid_3d(grid):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    # Ensure ax is Axes3D
    if not isinstance(ax, Axes3D):
        ax = Axes3D(fig)
    dx = dy = 0.8
    dz_unit = 0.5

    bar_bin_map = {}
    bin_pos_map = {}
    path_line = []

    for x in range(grid.width):
        for y in range(grid.depth):
            stack = grid.get_stack(x, y)
            for z, bin_item in enumerate(stack.bins):
                bar = ax.bar3d(
                    x, y, z * dz_unit,
                    dx, dy, dz_unit,
                    color=bin_item.color,
                    edgecolor='black',
                    alpha=0.9
                )
                bar.set_picker(True)
                bar_bin_map[bar] = (bin_item, (x, y, z))
                bin_pos_map[(x, y, z)] = bar

    def find_top_bin(x, y):
        stack = grid.get_stack(x, y)
        if stack.current_height > 0:
            return (x, y, stack.current_height - 1)
        return None

    def on_pick(event):
        artist = event.artist
        if artist in bar_bin_map:
            bin_item, (gx, gy, gz) = bar_bin_map[artist]
            start = find_top_bin(0, 0)
            goal = (gx, gy, gz)

            if start is None:
                print("No valid start bin.")
                return

            if path_line:
                path_line[0].remove()
                path_line.clear()

            for bar in bar_bin_map:
                bar.set_color('lightgrey')
                bar.set_edgecolor('black')

            path = astar_2d_then_down(start, goal, grid)
            if path:
                xs = [p[0] + dx / 2 for p in path]
                ys = [p[1] + dy / 2 for p in path]
                zs = [p[2] * dz_unit + dz_unit / 2 for p in path]
                line, = ax.plot(xs, ys, zs, color='black', linewidth=3, marker='o', alpha=0.9)
                path_line.append(line)

                for i, pos in enumerate(path):
                    if pos in bin_pos_map:
                        bar = bin_pos_map[pos]
                        if i == 0:
                            bar.set_color('green')
                            bar.set_edgecolor('yellow')
                        elif i == len(path) - 1:
                            bar.set_color('blue')
                            bar.set_edgecolor('orange')
                        else:
                            bar.set_color('red')
                            bar.set_edgecolor('black')

            plt.draw()

    fig.canvas.mpl_connect('pick_event', on_pick)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("AutoStore Grid Pathfinding")
    ax.set_xticks(range(grid.width))
    ax.set_yticks(range(grid.depth))
    plt.show()

# --- Main ---
if __name__ == "__main__":
    GRID_WIDTH = 10
    GRID_DEPTH = 10
    STACK_MAX_HEIGHT = 6
    spacing = 1.2

    autostore_grid = Grid(width=GRID_WIDTH, depth=GRID_DEPTH, stack_height=STACK_MAX_HEIGHT)
    visualize_grid_3d(autostore_grid)

    ws_base = [vector(GRID_WIDTH+1, 1, 0), vector(GRID_WIDTH+2, 2, 0), vector(GRID_WIDTH+1, 3, 0)]
    v0 = vertex(pos=ws_base[0], color=color.green, opacity=0.9)
    v1 = vertex(pos=ws_base[1], color=color.green, opacity=0.9)
    v2 = vertex(pos=ws_base[2], color=color.green, opacity=0.9)
    workstation = triangle(vs=[v0, v1, v2])

    # ---------- Create Robot ----------
    robot = sphere(radius=0.4, color=color.red, make_trail=True, trail_color=color.cyan, opacity=0.9)

    # ---------- Example Path (replace with A* for real sim) ----------
    path = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3)]

    # ---------- Animate Robot Movement ----------
    boxes = {}
    for x in range(GRID_WIDTH):
        for y in range(GRID_DEPTH):
            for z in range(STACK_MAX_HEIGHT):
                b = box(pos=vector(x * spacing, y * spacing, z * spacing),
                        size=vector(1, 1, 1),
                        color=color.white,
                        opacity=0.15)
                boxes[(x, y, z)] = b

    for pos in path:
        x, y, z = pos
        robot.pos = vector(x * spacing, y * spacing, z * spacing)
        current_box = boxes[(x, y, z)]
        current_box.color = color.yellow
        current_box.opacity = 0.5
        rate(1)
        current_box.color = color.white
        current_box.opacity = 0.15
        

    # Keep the scene alive
    while True:
        rate(60) 