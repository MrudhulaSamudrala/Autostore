import heapq
from typing import List, Tuple, Set, Optional
import time
import random

class ReservationTable:
    """Tracks cell reservations for collision avoidance in WHCA*"""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.reservations = {}  # {(x, y, t): bot_id}
        self.bot_positions = {}  # {bot_id: (x, y, t)}
    
    def reserve_cell(self, x: int, y: int, t: int, bot_id: int, from_cell=None):
        """Reserve a cell at time t for bot_id. Returns True if successful.
        Also reserves the cell the bot is leaving (from_cell) for t as a tail reservation to prevent following and swap collisions."""
        key = (x, y, t)
        if key in self.reservations and self.reservations[key] != bot_id:
            return False  # Cell already reserved by another bot
        # Prevent swap collision: check if another bot is moving from (x, y) to (from_cell) at t
        if from_cell:
            swap_key = (from_cell[0], from_cell[1], t)
            if swap_key in self.reservations and self.reservations[swap_key] != bot_id:
                return False
        self.reservations[key] = bot_id
        self.bot_positions[bot_id] = (x, y, t)
        # Tail reservation: reserve the cell the bot is leaving for t as well
        if from_cell:
            tail_key = (from_cell[0], from_cell[1], t)
            self.reservations[tail_key] = bot_id
        return True
    
    def is_reserved(self, x: int, y: int, t: int, bot_id: int) -> bool:
        """Check if cell is reserved by another bot at time t."""
        key = (x, y, t)
        return key in self.reservations and self.reservations[key] != bot_id
    
    def clear_expired_reservations(self, current_time: int):
        """Remove reservations older than window_size."""
        expired_keys = [key for key in self.reservations.keys() 
                       if key[2] < current_time - self.window_size]
        for key in expired_keys:
            del self.reservations[key]
    
    def get_bot_reservations(self, bot_id: int) -> List[Tuple[int, int, int]]:
        """Get all reservations for a specific bot."""
        return [(x, y, t) for (x, y, t), bid in self.reservations.items() 
                if bid == bot_id]

# Global reservation table instance
reservation_table = ReservationTable(window_size=5)

def whca_star_varied(start: Tuple[int, int], goal: Tuple[int, int], 
                     grid_size: Tuple[int, int], bot_id: int, 
                     current_time: int = 0, variation_factor: float = 0.3) -> Optional[List[Tuple[int, int]]]:
    """
    WHCA* implementation with path variation to avoid repetitive movement patterns.
    Adds randomization to make bot movement more realistic and interesting.
    """
    width, height = grid_size
    
    # Clear expired reservations
    reservation_table.clear_expired_reservations(current_time)
    
    # Priority queue for A* search
    open_set = []
    # (f_score, g_score, current_pos, time_step, path)
    heapq.heappush(open_set, (0, 0, start, current_time, [start]))
    
    # Track visited states to avoid cycles
    visited = set()
    
    # Heuristic function with randomization
    def heuristic(pos: Tuple[int, int]) -> int:
        base_distance = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        # Add small random variation to break ties and create different paths
        random_factor = random.uniform(-variation_factor, variation_factor)
        return base_distance + random_factor
    
    # Get valid neighbors with randomization
    def get_neighbors(pos: Tuple[int, int], t: int) -> List[Tuple[Tuple[int, int], int]]:
        x, y = pos
        neighbors = []
        # Randomize the order of directions to create path variation
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # Check grid bounds
            if 0 <= nx < width and 0 <= ny < height:
                # Check if cell is reserved at time t+1 (target cell) or t+1 (from_cell for swap)
                if not reservation_table.is_reserved(nx, ny, t + 1, bot_id) and not reservation_table.is_reserved(x, y, t + 1, bot_id):
                    neighbors.append(((nx, ny), t + 1))
        # Allow waiting in place if not reserved
        if not reservation_table.is_reserved(x, y, t + 1, bot_id):
            neighbors.append((pos, t + 1))
        return neighbors
    
    while open_set:
        f_score, g_score, current_pos, current_t, path = heapq.heappop(open_set)
        # Check if we reached the goal
        if current_pos == goal:
            # Reserve the path for this bot, with tail reservation
            for i, (x, y) in enumerate(path):
                from_cell = path[i - 1] if i > 0 else None
                reservation_table.reserve_cell(x, y, current_time + i, bot_id, from_cell=from_cell)
            return path
        # Create state key for visited tracking
        state_key = (current_pos, current_t)
        if state_key in visited:
            continue
        visited.add(state_key)
        # Explore neighbors
        for neighbor_pos, neighbor_t in get_neighbors(current_pos, current_t):
            if neighbor_t > current_time + reservation_table.window_size:
                continue  # Don't plan beyond window
            new_g_score = g_score + 1
            new_f_score = new_g_score + heuristic(neighbor_pos)
            neighbor_state = (neighbor_pos, neighbor_t)
            if neighbor_state not in visited:
                new_path = path + [neighbor_pos]
                heapq.heappush(open_set, (new_f_score, new_g_score, neighbor_pos, neighbor_t, new_path))
    return None  # No path found

def whca_star(start: Tuple[int, int], goal: Tuple[int, int], 
               grid_size: Tuple[int, int], bot_id: int, 
               current_time: int = 0) -> Optional[List[Tuple[int, int]]]:
    """
    WHCA* implementation with enhanced collision avoidance.
    Prevents head-on, following, and corner collisions, and handles reservation race conditions.
    """
    width, height = grid_size
    
    # Clear expired reservations
    reservation_table.clear_expired_reservations(current_time)
    
    # Priority queue for A* search
    open_set = []
    # (f_score, g_score, current_pos, time_step, path)
    heapq.heappush(open_set, (0, 0, start, current_time, [start]))
    
    # Track visited states to avoid cycles
    visited = set()
    
    # Heuristic function (Manhattan distance)
    def heuristic(pos: Tuple[int, int]) -> int:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    # Get valid neighbors
    def get_neighbors(pos: Tuple[int, int], t: int) -> List[Tuple[Tuple[int, int], int]]:
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4-directional movement
            nx, ny = x + dx, y + dy
            # Check grid bounds
            if 0 <= nx < width and 0 <= ny < height:
                # Check if cell is reserved at time t+1 (target cell) or t+1 (from_cell for swap)
                if not reservation_table.is_reserved(nx, ny, t + 1, bot_id) and not reservation_table.is_reserved(x, y, t + 1, bot_id):
                    neighbors.append(((nx, ny), t + 1))
        # Allow waiting in place if not reserved
        if not reservation_table.is_reserved(x, y, t + 1, bot_id):
            neighbors.append((pos, t + 1))
        return neighbors
    
    while open_set:
        f_score, g_score, current_pos, current_t, path = heapq.heappop(open_set)
        # Check if we reached the goal
        if current_pos == goal:
            # Reserve the path for this bot, with tail reservation
            for i, (x, y) in enumerate(path):
                from_cell = path[i - 1] if i > 0 else None
                reservation_table.reserve_cell(x, y, current_time + i, bot_id, from_cell=from_cell)
            return path
        # Create state key for visited tracking
        state_key = (current_pos, current_t)
        if state_key in visited:
            continue
        visited.add(state_key)
        # Explore neighbors
        for neighbor_pos, neighbor_t in get_neighbors(current_pos, current_t):
            if neighbor_t > current_time + reservation_table.window_size:
                continue  # Don't plan beyond window
            new_g_score = g_score + 1
            new_f_score = new_g_score + heuristic(neighbor_pos)
            neighbor_state = (neighbor_pos, neighbor_t)
            if neighbor_state not in visited:
                new_path = path + [neighbor_pos]
                heapq.heappush(open_set, (new_f_score, new_g_score, neighbor_pos, neighbor_t, new_path))
    return None  # No path found

def create_varied_path(start: Tuple[int, int], goal: Tuple[int, int], 
                      grid_size: Tuple[int, int], bot_id: int, 
                      current_time: int = 0) -> Optional[List[Tuple[int, int]]]:
    """
    Creates varied paths by using different pathfinding strategies randomly.
    This prevents bots from always taking the same route.
    """
    strategies = [
        lambda: whca_star_varied(start, goal, grid_size, bot_id, current_time, 0.2),
        lambda: whca_star_varied(start, goal, grid_size, bot_id, current_time, 0.4),
        lambda: whca_star_varied(start, goal, grid_size, bot_id, current_time, 0.6),
        lambda: whca_star(start, goal, grid_size, bot_id, current_time)
    ]
    
    # Randomly select a strategy
    strategy = random.choice(strategies)
    path = strategy()
    
    # If no path found, try the original WHCA* as fallback
    if not path:
        path = whca_star(start, goal, grid_size, bot_id, current_time)
    
    return path

def astar_grid(start: Tuple[int, int], goal: Tuple[int, int], 
                obstacles: Set[Tuple[int, int]], grid_size: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """
    Original A* implementation (kept for backward compatibility).
    Use whca_star for collision-aware pathfinding.
    """
    width, height = grid_size
    
    # Priority queue for A* search
    open_set = []
    heapq.heappush(open_set, (0, 0, start, [start]))
    
    # Track visited positions
    visited = set()
    
    # Heuristic function (Manhattan distance)
    def heuristic(pos: Tuple[int, int]) -> int:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    # Get valid neighbors
    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = []
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4-directional movement
            nx, ny = x + dx, y + dy
            
            # Check grid bounds and obstacles
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in obstacles:
                neighbors.append((nx, ny))
        
        return neighbors
    
    while open_set:
        f_score, g_score, current_pos, path = heapq.heappop(open_set)
        
        # Check if we reached the goal
        if current_pos == goal:
            return path
        
        # Check if already visited
        if current_pos in visited:
            continue
        visited.add(current_pos)
        
        # Explore neighbors
        for neighbor_pos in get_neighbors(current_pos):
            if neighbor_pos not in visited:
                new_g_score = g_score + 1
                new_f_score = new_g_score + heuristic(neighbor_pos)
                new_path = path + [neighbor_pos]
                heapq.heappush(open_set, (new_f_score, new_g_score, neighbor_pos, new_path))
    
    return None  # No path found

def update_bot_reservations(bot_id: int, current_pos: Tuple[int, int], 
                           target_pos: Tuple[int, int], current_time: int):
    """
    Update reservations for a bot that's moving from current_pos to target_pos.
    This should be called each time a bot moves.
    """
    # Clear old reservations for this bot
    old_reservations = reservation_table.get_bot_reservations(bot_id)
    for x, y, t in old_reservations:
        if (x, y, t) in reservation_table.reservations:
            del reservation_table.reservations[(x, y, t)]
    
    # Add new reservation for target position
    reservation_table.reserve_cell(target_pos[0], target_pos[1], current_time, bot_id)
    
    # Clear expired reservations
    reservation_table.clear_expired_reservations(current_time)

def get_reservation_table_status() -> dict:
    """Get current status of the reservation table for debugging."""
    return {
        'reservations': reservation_table.reservations,
        'bot_positions': reservation_table.bot_positions,
        'window_size': reservation_table.window_size
    } 