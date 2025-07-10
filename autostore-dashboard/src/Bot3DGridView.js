import React, { useEffect, useState, useRef, useMemo } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls as DreiOrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { Html } from '@react-three/drei';

const DEFAULT_GRID_SIZE = 6;
const DEFAULT_GRID_HEIGHT = 6;
const DEFAULT_BOT_COUNT = 8;
const DEFAULT_BOT_SPEED = 1.2;
const binColors = [
  0x4a90e2, 0x7b68ee, 0x20b2aa, 0x32cd32, 0xff6347, 0xffb800, 0xff3366, 0x00ffcc, 0x0088ff, 0x8aff80
];
const BOT_STATES = ['idle', 'moving', 'digging', 'carrying'];
const INDICATOR_COLORS = {
  idle: 0x64748b,
  moving: 0x00ff88,
  digging: 0xffb800,
  carrying: 0xff3366,
};

// Adjusted grid spacing and sizes for clarity
const CELL_SIZE = 3;
const POST_SIZE = 0.15;
const RAIL_HEIGHT = 0.2;
const BIN_SIZE = 2.5;
const BOT_SIZE = 1.7;

function GridFramework({ gridSize, gridHeight }) {
  const posts = [];
  for (let x = 0; x <= gridSize; x++) {
    for (let z = 0; z <= gridSize; z++) {
      posts.push(
        <mesh key={`post-${x}-${z}`} position={[x * CELL_SIZE - (gridSize * CELL_SIZE) / 2, gridHeight * CELL_SIZE / 2, z * CELL_SIZE - (gridSize * CELL_SIZE) / 2]} castShadow={false} receiveShadow={false}>
          <boxGeometry args={[POST_SIZE, gridHeight * CELL_SIZE, POST_SIZE]} />
          <meshPhongMaterial color={0xe6e6fa} shininess={300} specular={0x666666} transparent opacity={0.95} />
        </mesh>
      );
    }
  }
  const railsX = [];
  for (let z = 0; z <= gridSize; z++) {
    railsX.push(
      <mesh key={`rail-x-${z}`} position={[0, gridHeight * CELL_SIZE + RAIL_HEIGHT / 2, z * CELL_SIZE - (gridSize * CELL_SIZE) / 2]} castShadow={false} receiveShadow={false}>
        <boxGeometry args={[gridSize * CELL_SIZE, RAIL_HEIGHT, RAIL_HEIGHT]} />
        <meshPhongMaterial color={0x00ffcc} shininess={200} specular={0x444444} emissive={0x003322} transparent opacity={0.9} />
      </mesh>
    );
  }
  const railsZ = [];
  for (let x = 0; x <= gridSize; x++) {
    railsZ.push(
      <mesh key={`rail-z-${x}`} position={[x * CELL_SIZE - (gridSize * CELL_SIZE) / 2, gridHeight * CELL_SIZE + RAIL_HEIGHT / 2, 0]} castShadow={false} receiveShadow={false}>
        <boxGeometry args={[RAIL_HEIGHT, RAIL_HEIGHT, gridSize * CELL_SIZE]} />
        <meshPhongMaterial color={0x00ffcc} shininess={200} specular={0x444444} emissive={0x003322} transparent opacity={0.9} />
      </mesh>
    );
  }
  return <>{posts}{railsX}{railsZ}</>;
}

function Bin({ x, y, z, color, gridSize, binId, productNames, isCarried }) {
  const binRef = useRef();
  const [hovered, setHovered] = useState(false);
  useEffect(() => {
    if (binRef.current) {
      binRef.current.material.color.setHex(color);
    }
  }, [color]);
  return (
    <group position={[
      x * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2,
      y * CELL_SIZE + BIN_SIZE / 2,
      z * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2
    ]}>
      <mesh ref={binRef} castShadow receiveShadow
        onPointerOver={isCarried ? () => setHovered(true) : undefined}
        onPointerOut={isCarried ? () => setHovered(false) : undefined}
      >
        <boxGeometry args={[BIN_SIZE, BIN_SIZE, BIN_SIZE]} />
        <meshStandardMaterial color={color} transparent opacity={0.92} emissive={color} emissiveIntensity={0.18} />
      </mesh>
      <lineSegments>
        <edgesGeometry attach="geometry" args={[new THREE.BoxGeometry(BIN_SIZE, BIN_SIZE, BIN_SIZE)]} />
        <lineBasicMaterial attach="material" color={0x00ffcc} transparent opacity={0.3} />
      </lineSegments>
      {isCarried && hovered && (
        <Html center style={{ pointerEvents: 'none', background: 'rgba(20,20,30,0.95)', color: '#fff', padding: '6px 12px', borderRadius: 8, fontSize: 15, fontWeight: 500, boxShadow: '0 2px 8px #0008' }}>
          <div>Bin #{binId}</div>
          {productNames && productNames.length > 0 ? (
            <div>Product: {productNames.join(', ')}</div>
          ) : (
            <div>No product</div>
          )}
        </Html>
      )}
    </group>
  );
}

// --- A* Pathfinding Utility ---
function astarGridJS(start, goal, gridSize) {
  // start, goal: [x, z] in grid coordinates
  // gridSize: [width, height]
  const openSet = [];
  openSet.push({ pos: start, f: 0, g: 0 });
  const cameFrom = {};
  const gScore = { [start.join(",")]: 0 };
  const fScore = { [start.join(",")]: manhattan(start, goal) };
  const closedSet = new Set();

  function manhattan(a, b) {
    return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
  }
  function neighbors([x, z]) {
    const result = [];
    for (const [dx, dz] of [[-1,0],[1,0],[0,-1],[0,1]]) {
      const nx = x + dx, nz = z + dz;
      if (nx >= 0 && nx < gridSize[0] && nz >= 0 && nz < gridSize[1]) {
        result.push([nx, nz]);
      }
    }
    return result;
  }

  while (openSet.length > 0) {
    openSet.sort((a, b) => a.f - b.f);
    const current = openSet.shift();
    const key = current.pos.join(",");
    if (current.pos[0] === goal[0] && current.pos[1] === goal[1]) {
      // Reconstruct path
      const path = [current.pos];
      let ckey = key;
      while (cameFrom[ckey]) {
        path.push(cameFrom[ckey]);
        ckey = cameFrom[ckey].join(",");
      }
      return path.reverse();
    }
    closedSet.add(key);
    for (const neighbor of neighbors(current.pos)) {
      const nkey = neighbor.join(",");
      if (closedSet.has(nkey)) continue;
      const tentative_g = gScore[key] + 1;
      if (!(nkey in gScore) || tentative_g < gScore[nkey]) {
        cameFrom[nkey] = current.pos;
        gScore[nkey] = tentative_g;
        fScore[nkey] = tentative_g + manhattan(neighbor, goal);
        if (!openSet.some(n => n.pos[0] === neighbor[0] && n.pos[1] === neighbor[1])) {
          openSet.push({ pos: neighbor, f: fScore[nkey], g: gScore[nkey] });
        }
      }
    }
  }
  return null;
}

function DetailedBot({ bot, gridSize, gridHeight, botSpeed, paused }) {
  // Always call hooks first
  const [step, setStep] = useState(0);
  const [pos, setPos] = useState(() => gridToWorld([bot.x % gridSize, bot.z % gridSize], gridSize, gridHeight));
  const [status, setStatus] = useState(bot.status);
  const speed = botSpeed * 0.07;

  function gridToWorld([gx, gz], gridSize, gridHeight) {
    return [
      gx * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2,
      gridHeight * CELL_SIZE + BOT_SIZE / 2,
      gz * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2
    ];
  }

  // Reset pos and step when path changes
  useEffect(() => {
    if (bot.path && bot.path.length > 0) {
      setStep(0);
      setPos(gridToWorld(bot.path[0], gridSize, gridHeight));
    }
  }, [bot.path, gridSize, gridHeight]);

  // Move along the backend path
  useFrame(() => {
    if (!bot.assigned_order_id || paused || !bot.path || bot.path.length === 0) return;
    const [tx, tz] = bot.path[step] || bot.path[bot.path.length - 1];
    let [x, y, z] = pos;
    const [wx, wy, wz] = gridToWorld([tx, tz], gridSize, gridHeight);
    const dx = wx - x, dz = wz - z;
    const dist = Math.sqrt(dx * dx + dz * dz);
    if (dist > 0.05) {
      x += (dx / dist) * speed;
      z += (dz / dist) * speed;
      setPos([x, y, z]);
      setStatus('moving');
    } else if (step < bot.path.length - 1) {
      setStep(step + 1);
    } else {
      setStatus(bot.status);
    }
  });

  // If bot is idle (no assigned order), keep it static at its current position
  if (!bot.assigned_order_id) {
    const staticPos = [
      bot.x * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2,
      gridHeight * CELL_SIZE + BOT_SIZE / 2,
      bot.z * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2
    ];
    const indicatorColor = INDICATOR_COLORS['idle'] || 0x64748b;
    const wheelPositions = [
      [-0.5, -0.2, -0.5],
      [0.5, -0.2, -0.5],
      [-0.5, -0.2, 0.5],
      [0.5, -0.2, 0.5],
    ];
    return (
      <group position={staticPos}>
        <mesh castShadow receiveShadow>
          <boxGeometry args={[BOT_SIZE, BOT_SIZE, BOT_SIZE]} />
          <meshPhongMaterial color={0xff0000} shininess={100} />
        </mesh>
        <mesh position={[0, BOT_SIZE / 2 - 0.2, 0.4]}>
          <cylinderGeometry args={[0.18, 0.18, 0.18, 16]} />
          <meshPhongMaterial color={indicatorColor} emissive={indicatorColor} emissiveIntensity={0.7} />
        </mesh>
        {wheelPositions.map((p, i) => (
          <mesh key={i} position={p} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.2, 0.2, 0.1, 12]} />
            <meshPhongMaterial color={0x333333} shininess={50} />
          </mesh>
        ))}
      </group>
    );
  }
  const indicatorColor = INDICATOR_COLORS[status] || 0x64748b;
  const wheelPositions = [
    [-0.5, -0.2, -0.5],
    [0.5, -0.2, -0.5],
    [-0.5, -0.2, 0.5],
    [0.5, -0.2, 0.5],
  ];

  return (
    <group position={pos}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[BOT_SIZE, BOT_SIZE, BOT_SIZE]} />
        <meshPhongMaterial color={0xff0000} shininess={100} />
      </mesh>
      <mesh position={[0, BOT_SIZE / 2 - 0.2, 0.4]}>
        <cylinderGeometry args={[0.18, 0.18, 0.18, 16]} />
        <meshPhongMaterial color={indicatorColor} emissive={indicatorColor} emissiveIntensity={0.7} />
      </mesh>
      {wheelPositions.map((p, i) => (
        <mesh key={i} position={p} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.2, 0.2, 0.1, 12]} />
          <meshPhongMaterial color={0x333333} shininess={50} />
        </mesh>
      ))}
    </group>
  );
}

function Bots({ botCount, gridSize, gridHeight, botSpeed, paused, setBotStatusList }) {
  // Simulate bots with random initial positions
  const bots = useMemo(() => {
    return Array.from({ length: botCount }, (_, i) => ({ id: i, x: Math.floor(Math.random() * gridSize), z: Math.floor(Math.random() * gridSize) }));
  }, [botCount, gridSize]);

  // Track status for status panel
  const [statuses, setStatuses] = useState(Array(botCount).fill('idle'));
  useEffect(() => {
    setBotStatusList(statuses);
  }, [statuses, setBotStatusList]);

  return bots.map((bot, i) => (
    <DetailedBot key={bot.id} bot={bot} gridSize={gridSize} gridHeight={gridHeight} botSpeed={botSpeed} paused={paused}
      setStatus={s => setStatuses(st => { const arr = [...st]; arr[i] = s; return arr; })} />
  ));
}

function PremiumLights() {
  return <>
    <ambientLight intensity={0.85} color={0x1a1a2e} />
    <hemisphereLight skyColor={0xffffff} groundColor={0x22223b} intensity={0.45} position={[0, 50, 0]} />
    <directionalLight
      castShadow
      position={[50, 100, 50]}
      intensity={1.1}
      shadow-mapSize-width={1024}
      shadow-mapSize-height={1024}
      shadow-camera-near={0.1}
      shadow-camera-far={200}
      shadow-camera-left={-50}
      shadow-camera-right={50}
      shadow-camera-top={50}
      shadow-camera-bottom={-50}
      color={0xffffff}
    />
    <pointLight position={[-25, 25, -25]} intensity={1.2} color={0x00ffcc} />
    <pointLight position={[25, 20, 25]} intensity={1.0} color={0x0088ff} />
    <pointLight position={[0, 30, 0]} intensity={0.7} color={0xff3366} />
  </>;
}

function DarkBackground() {
  const { gl } = useThree();
  useEffect(() => {
    gl.setClearColor(new THREE.Color(0x050510));
  }, [gl]);
  return null;
}

function WebGLContextLossHandler() {
  const { gl } = useThree();
  useEffect(() => {
    const handle = () => alert('WebGL context lost. Please refresh the page.');
    gl.domElement.addEventListener('webglcontextlost', handle);
    return () => gl.domElement.removeEventListener('webglcontextlost', handle);
  }, [gl]);
  return null;
}

function CenteredOrbitControls({ gridSize, gridHeight }) {
  const { camera, gl, controls } = useThree();
  const controlsRef = useRef();
  useEffect(() => {
    const center = [0, (gridHeight * CELL_SIZE) / 2, 0];
    if (controlsRef.current) {
      controlsRef.current.target.set(...center);
      controlsRef.current.update();
    }
  }, [gridSize, gridHeight]);
  return (
    <DreiOrbitControls
      ref={controlsRef}
      enablePan
      enableZoom
      enableRotate
      minDistance={CELL_SIZE * 3}
      maxDistance={CELL_SIZE * 20}
      maxPolarAngle={Math.PI / 1.8}
      args={[camera, gl.domElement]}
    />
  );
}

function SpecialStations({ gridSize, gridHeight }) {
  // Parking stations: (5,5), (5,4); Delivery station: (5,0)
  const stations = [
    { x: gridSize - 1, z: gridSize - 1, color: 0xff66cc, label: 'Parking 1' },
    { x: gridSize - 1, z: gridSize - 2, color: 0xff66cc, label: 'Parking 2' },
    { x: gridSize - 1, z: 0, color: 0x00ffff, label: 'Delivery' },
  ];
  return (
    <>
      {stations.map((s, i) => (
        <group key={i} position={[
          s.x * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2,
          gridHeight * CELL_SIZE + 1.5,
          s.z * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2
        ]}>
          <mesh>
            <boxGeometry args={[2.9, 0.5, 2.9]} />
            <meshPhongMaterial color={s.color} transparent opacity={0.45} />
          </mesh>
          <Html center style={{ pointerEvents: 'none', color: '#fff', fontWeight: 700, fontSize: 16, textShadow: '0 2px 8px #0008' }}>{s.label}</Html>
        </group>
      ))}
    </>
  );
}

export default function Bot3DGridView() {
  // Controls state
  const [gridSize, setGridSize] = useState(DEFAULT_GRID_SIZE);
  const [gridHeight, setGridHeight] = useState(DEFAULT_GRID_HEIGHT);
  const [botCount, setBotCount] = useState(DEFAULT_BOT_COUNT); // Always reflect backend
  const [botSpeed, setBotSpeed] = useState(DEFAULT_BOT_SPEED);
  const [paused, setPaused] = useState(false);
  const [binSeed, setBinSeed] = useState(0);
  const [botStatusList, setBotStatusList] = useState(Array(DEFAULT_BOT_COUNT).fill('idle'));

  // Real data state
  const [bots, setBots] = useState([]);
  const [bins, setBins] = useState([]);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);

  // WebSocket for bots
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/bots');
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setBots(prev => {
          // Only update if changed
          if (JSON.stringify(prev) !== JSON.stringify(data)) {
            setBotCount(data.length); // Always sync botCount
            return data;
          }
          return prev;
        });
      } catch (e) {}
    };
    ws.onerror = (e) => {};
    return () => ws.close();
  }, []);

  // Poll bins, orders, products (unless websocket available)
  useEffect(() => {
    const fetchAll = () => {
      fetch('http://localhost:8000/bins/').then(res => res.json()).then(setBins);
      fetch('http://localhost:8000/orders/').then(res => res.json()).then(setOrders);
      fetch('http://localhost:8000/products/').then(res => res.json()).then(setProducts);
    };
    fetchAll();
    const interval = setInterval(fetchAll, 2000); // poll every 2s
    return () => clearInterval(interval);
  }, [binSeed]);

  // Map bin id to product names
  const binIdToProductNames = useMemo(() => {
    const map = {};
    products.forEach(p => {
      if (!map[p.bin_id]) map[p.bin_id] = [];
      map[p.bin_id].push(p.name);
    });
    return map;
  }, [products]);

  // Determine which bins are being carried by bots
  const carriedBinIds = useMemo(() => {
    const ids = new Set();
    bots.forEach(bot => {
      if (bot.status === 'carrying' && bot.destination_bin && bot.destination_bin.length > 0) {
        // Assume bot.destination_bin[3] is bin id, or use a field if available
        if (bot.destination_bin.bin_id) {
          ids.add(bot.destination_bin.bin_id);
        } else if (bot.destination_bin[3]) {
          ids.add(bot.destination_bin[3]);
        }
      }
    });
    return ids;
  }, [bots]);

  // System status (use real bins if available)
  const totalCells = gridSize * gridSize;
  const totalBins = bins.length;
  const density = totalBins && totalCells ? (totalBins / totalCells).toFixed(1) : '0';
  const activeRobots = bots.filter(b => b.status === 'moving').length;

  // Handlers
  const handleResetGrid = () => setBinSeed(s => s + 1);

  // Render bins from real data
  function BinsFromState() {
    return <>{bins.map((bin, i) => (
      <Bin key={`bin-${bin.id || i}`}
        x={bin.x} y={bin.y} z={bin.z_location}
        color={binColors[i % binColors.length]}
        gridSize={gridSize}
        binId={bin.id}
        productNames={binIdToProductNames[bin.id] || []}
        isCarried={carriedBinIds.has(bin.id)}
      />
    ))}</>;
  }

  // Only render real bots from backend
  function BotsFromState() {
    return <>
      {bots.map((bot, i) => (
        <DetailedBot
          key={`bot-${bot.id}`}
          bot={bot}
          gridSize={gridSize}
          gridHeight={gridHeight}
          botSpeed={botSpeed}
          paused={paused}
          setStatus={s => setBotStatusList(st => { const arr = [...st]; arr[i] = s; return arr; })}
        />
      ))}
    </>;
  }

  return (
    <div className="w-full h-[calc(100vh-120px)] flex flex-row items-center justify-center bg-gradient-to-br from-[#0a0a0f] via-[#1a1a2e] to-[#0f0f23] rounded-xl shadow-xl p-6 box-border">
      {/* Left Panel */}
      <div
        className="bg-[#15152a] bg-opacity-95 border border-cyan-400/30 rounded-2xl shadow-xl p-6 m-6 min-w-[260px] max-w-xs flex-shrink-0 text-base"
        style={{
          background: 'rgba(21,21,42,0.95)',
          border: '1px solid rgba(0,255,200,0.3)',
          borderRadius: '1rem',
          boxShadow: '0 8px 32px rgba(0,255,200,0.1)',
          padding: '1.5rem',
          margin: '1.5rem',
          minWidth: 260,
          maxWidth: 340,
        }}
      >
        <h3 className="text-white text-xl font-bold mb-4">Grid Controller</h3>
        <div className="mb-4">
          <label className="block text-gray-300 mb-1">Grid Size: <span className="text-cyan-300 font-bold">{gridSize}x{gridSize}</span></label>
          <input type="range" min={4} max={16} value={gridSize} onChange={e => setGridSize(Number(e.target.value))} className="w-full" />
        </div>
        <div className="mb-4">
          <label className="block text-gray-300 mb-1">Grid Height: <span className="text-cyan-300 font-bold">{gridHeight} levels</span></label>
          <input type="range" min={4} max={16} value={gridHeight} onChange={e => setGridHeight(Number(e.target.value))} className="w-full" />
        </div>
        <button onClick={handleResetGrid} className="w-full bg-cyan-400 hover:bg-cyan-500 text-[#15152a] font-bold py-2 rounded-lg mb-6 transition text-base">Reset Grid</button>
        <h3 className="text-white text-xl font-bold mb-4">Bot Controller</h3>
        <div className="mb-4">
          <label className="block text-gray-300 mb-1">Bot Count: <span className="text-cyan-300 font-bold">{botCount} robots</span></label>
          <input type="range" min={1} max={24} value={botCount} onChange={e => { setBotCount(Number(e.target.value)); setBotStatusList(Array(Number(e.target.value)).fill('idle')); }} className="w-full" />
        </div>
        <div className="mb-4">
          <label className="block text-gray-300 mb-1">Bot Speed: <span className="text-cyan-300 font-bold">{botSpeed.toFixed(1)}x</span></label>
          <input type="range" min={0.5} max={3} step={0.1} value={botSpeed} onChange={e => setBotSpeed(Number(e.target.value))} className="w-full" />
        </div>
        <button onClick={() => setPaused(p => !p)} className={`w-full font-bold py-2 rounded-lg transition text-base ${paused ? 'bg-pink-500 text-white' : 'bg-green-400 text-[#15152a]'}`}>{paused ? 'Play' : 'Pause'}</button>
      </div>
      {/* 3D Visualization Centered */}
      <div className="flex-1 flex items-center justify-center min-w-0 max-w-[1000px] max-h-[1000px] w-full h-full aspect-square overflow-hidden">
        <Canvas camera={{ position: [0, 1.5 * gridSize * CELL_SIZE, 1.5 * gridSize * CELL_SIZE], fov: 60 }} shadows>
          <DarkBackground />
          <WebGLContextLossHandler />
          <PremiumLights />
          <GridFramework gridSize={gridSize} gridHeight={gridHeight} />
          <SpecialStations gridSize={gridSize} gridHeight={gridHeight} />
          <BinsFromState />
          <BotsFromState />
          <CenteredOrbitControls gridSize={gridSize} gridHeight={gridHeight} />
        </Canvas>
      </div>
      {/* Right Panel */}
      <div
        className="bg-[#15152a] bg-opacity-95 border border-cyan-400/30 rounded-2xl shadow-xl p-6 m-6 min-w-[260px] max-w-xs flex-shrink-0 text-base"
        style={{
          background: 'rgba(21,21,42,0.95)',
          border: '1px solid rgba(0,255,200,0.3)',
          borderRadius: '1rem',
          boxShadow: '0 8px 32px rgba(0,255,200,0.1)',
          padding: '1.5rem',
          margin: '1.5rem',
          minWidth: 260,
          maxWidth: 340,
        }}
      >
        <h3 className="text-white text-xl font-bold mb-4">System Status</h3>
        <div className="mb-2 flex justify-between text-gray-300"><span>Grid Cells:</span><span className="text-cyan-300 font-bold">{totalCells}</span></div>
        <div className="mb-2 flex justify-between text-gray-300"><span>Total Bins:</span><span className="text-cyan-300 font-bold">{totalBins}</span></div>
        <div className="mb-2 flex justify-between text-gray-300"><span>Storage Density:</span><span className="text-cyan-300 font-bold">{density}x</span></div>
        <div className="mb-2 flex justify-between text-gray-300"><span>Active Robots:</span><span className="text-cyan-300 font-bold">{activeRobots}</span></div>
        <h4 className="text-white text-lg font-bold mt-6 mb-2">Bot Status</h4>
        <div className="space-y-1">
          {bots.map((bot, i) => (
            <div key={bot.id} className="bg-slate-800 rounded px-3 py-1 mb-1 text-slate-100 text-sm font-mono">
              Robot {i + 1}: {bot.status ? bot.status.toUpperCase() : 'IDLE'}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 