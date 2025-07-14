import React, { useEffect, useState, useRef, useMemo } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls as DreiOrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { Html } from '@react-three/drei';
import axios from 'axios';

const DEFAULT_GRID_SIZE = 6;
const DEFAULT_GRID_HEIGHT = 6;
const DEFAULT_BOT_COUNT = 8;
const DEFAULT_BOT_SPEED = 0.1; // or even 0.05 for ultra-slow
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

function Bin({ x, y, z, color, gridSize, binId, productNames, isCarried, style }) {
  const binRef = useRef();
  const [hovered, setHovered] = useState(false);
  useEffect(() => {
    if (binRef.current) {
      binRef.current.material.color.setHex(color);
    }
  }, [color]);
  // If isCarried, don't render the bin in the grid
  if (isCarried) return null;
  return (
    <group position={[
      x * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2,
      y * CELL_SIZE + BIN_SIZE / 2,
      z * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2
    ]} style={style}>
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

// Single gridToWorld function for all usage
function gridToWorld([gx, gy], gridSize, gridHeight) {
  const CELL_SIZE = 3;
  const BOT_SIZE = 1.7;
  return [
    gx * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2,
    gridHeight * CELL_SIZE + BOT_SIZE / 2,
    gy * CELL_SIZE - (gridSize * CELL_SIZE) / 2 + CELL_SIZE / 2
  ];
}

function DetailedBot({ bot, gridSize, gridHeight }) {
  // Parking positions for each bot
  const parkingPositions = {
    1: [5, 5],
    2: [5, 4],
    // Add more if needed
  };
  const [position, setPosition] = useState(() =>
    gridToWorld([bot.x, bot.y], gridSize, gridHeight)
  );
  const [carriedBin, setCarriedBin] = useState(null);
  const [currentPath, setCurrentPath] = useState([]);

  useEffect(() => {
    // Update position when bot moves
    setPosition(gridToWorld([bot.x, bot.y], gridSize, gridHeight));
    // Update carried bin
    setCarriedBin(bot.carried_bin_id ? {
      id: bot.carried_bin_id,
      color: binColors[bot.carried_bin_id % binColors.length]
    } : null);
    // Animate path if changed
    if (bot.path && !pathsAreEqual(bot.path, currentPath)) {
      setCurrentPath(bot.path);
      animatePath(bot.path);
    }
  }, [bot.x, bot.y, bot.path, bot.carried_bin_id]);

  const animatePath = (path) => {
    let step = 0;
    const animate = () => {
      if (step >= path.length) return;
      const [x, y] = path[step];
      setPosition(gridToWorld([x, y], gridSize, gridHeight));
      step++;
      if (step < path.length) {
        requestAnimationFrame(animate);
      }
    };
    animate();
  };

  // Always show bot at parking when idle
  const isIdle = bot.status === 'idle';
  const [parkX, parkY] = parkingPositions[bot.id] || [5, 0];
  const displayPos = isIdle
    ? gridToWorld([parkX, parkY], gridSize, gridHeight)
    : position;

  return (
    <group position={displayPos}>
      {/* Path visualization */}
      {currentPath && currentPath.length > 1 && (
        <line>
          <bufferGeometry
            attach="geometry"
            setFromPoints={currentPath.map(([x, y]) =>
              new THREE.Vector3(...gridToWorld([x, y], gridSize, gridHeight))
            )}
          />
          <lineBasicMaterial attach="material" color={0xffff00} linewidth={2} />
        </line>
      )}
      {/* Bot model */}
      <mesh castShadow receiveShadow>
        <boxGeometry args={[BOT_SIZE, BOT_SIZE, BOT_SIZE]} />
        <meshStandardMaterial color={bot.id === 1 ? 0xff0000 : 0x0000ff} />
      </mesh>
      {/* Carried bin */}
      {carriedBin && (
        <group position={[0, BOT_SIZE/2 + BIN_SIZE/2, 0]}>
          <mesh castShadow receiveShadow>
            <boxGeometry args={[BIN_SIZE, BIN_SIZE, BIN_SIZE]} />
            <meshStandardMaterial 
              color={carriedBin.color} 
              transparent 
              opacity={0.9}
            />
          </mesh>
        </group>
      )}
      {/* Status indicator */}
      <Html center>
        <div style={{
          background: 'rgba(0,0,0,0.7)',
          color: '#fff',
          padding: '4px 8px',
          borderRadius: 4,
          fontSize: 12,
          whiteSpace: 'nowrap'
        }}>
          Bot {bot.id}: {bot.status}
        </div>
      </Html>
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
    <DetailedBot key={bot.id} bot={bot} gridSize={gridSize} gridHeight={gridHeight}
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

function botsAreEqual(botsA, botsB) {
  return JSON.stringify(botsA) === JSON.stringify(botsB);
}

function pathsAreEqual(pathA, pathB) {
  if (!Array.isArray(pathA) || !Array.isArray(pathB)) return false;
  if (pathA.length !== pathB.length) return false;
  for (let i = 0; i < pathA.length; i++) {
    if (pathA[i][0] !== pathB[i][0] || pathA[i][1] !== pathB[i][1]) return false;
  }
  return true;
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
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [started, setStarted] = useState(false);
  const [returningBins, setReturningBins] = useState({});

  // Real data state
  const [bots, setBots] = useState([]);
  const [bins, setBins] = useState([]);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);

  // Define fetchBots at the top level of the component
  const fetchBots = () => {
    fetch('http://localhost:8000/bots/')
      .then(res => res.json())
      .then(data => setBots(data))
      .catch(err => console.error('Failed to fetch bots:', err));
  };

  // Add this after bots state is defined
  useEffect(() => {
    // console.log('Current bots:', bots); // Removed to reduce console spam
  }, [bots]);

  // Fetch bots from the new /bots/ endpoint
  useEffect(() => {
    fetchBots();
    // Only poll if WebSocket is not connected
    if (connectionStatus !== 'connected') {
      const interval = setInterval(fetchBots, 1000); // poll every 1s
      return () => clearInterval(interval);
    }
  }, [connectionStatus]);

  // Poll bins, orders, products (unless websocket available)
  useEffect(() => {
    const fetchAll = () => {
      fetch('http://127.0.0.1:8000/bins/').then(res => res.json()).then(setBins);
      fetch('http://127.0.0.1:8000/orders/').then(res => res.json()).then(setOrders);
      fetch('http://127.0.0.1:8000/products/').then(res => res.json()).then(setProducts);
    };
    fetchAll();
    // Only poll if WebSocket is not connected, and reduce frequency
    if (connectionStatus !== 'connected') {
      const interval = setInterval(fetchAll, 5000); // poll every 5s instead of 2s
      return () => clearInterval(interval);
    }
  }, [binSeed, connectionStatus]);

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

  // Track bins dropped at delivery station
  const [deliveredBins, setDeliveredBins] = useState([]);

  // Watch bots and update deliveredBins when a bin is dropped
  useEffect(() => {
    bots.forEach(bot => {
      // If bot just finished delivering (status is not 'carrying' or 'delivering', but was previously carrying this bin)
      if (
        bot.lastDeliveredBin &&
        !deliveredBins.includes(bot.lastDeliveredBin)
      ) {
        setDeliveredBins(prev => [...prev, bot.lastDeliveredBin]);
      }
    });
    // eslint-disable-next-line
  }, [bots]);

  // System status (use real bins if available)
  const totalCells = gridSize * gridSize;
  const totalBins = bins.length;
  const density = totalBins && totalCells ? (totalBins / totalCells).toFixed(1) : '0';
  const activeRobots = bots.filter(b => b.status === 'moving').length;

  // Handlers
  const handleResetGrid = () => setBinSeed(s => s + 1);

  // Handler to start bot movement
  // const handleStart = async () => {
  //   await axios.post('http://localhost:8000/orders/start-processing');
  //   setStarted(true);
  // };

  // Add this handler in Bot3DGridView:
  const handleForceRefreshBins = () => {
    fetch('http://127.0.0.1:8000/bins/')
      .then(res => res.json())
      .then(setBins)
      .catch(err => console.error('Failed to force refresh bins:', err));
  };

  // Render bins from real data
  function BinsFromState() {
    const carriedBinIds = new Set(
      bots.filter(b => b.carried_bin_id).map(b => b.carried_bin_id)
    );
    const deliveredBinIds = new Set(deliveredBins);

    return (
      <>
        {bins.map(bin => {
          // Hide bins being carried
          if (carriedBinIds.has(bin.id)) return null;
          // Show delivered bins at delivery station
          if (deliveredBinIds.has(bin.id)) {
            return (
              <Bin
                key={`delivered-${bin.id}`}
                x={5} y={0} z={0}
                color={binColors[bin.id % binColors.length]}
                gridSize={gridSize}
                binId={bin.id}
                isCarried={false}
              />
            );
          }
          // Show bins at grid position
          return (
            <Bin
              key={`bin-${bin.id}`}
              x={bin.x}
              y={bin.y}
              z={bin.z_location}
              color={binColors[bin.id % binColors.length]}
              gridSize={gridSize}
              binId={bin.id}
              isCarried={false}
            />
          );
        })}
      </>
    );
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

  useEffect(() => {
    let ws;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000; // 3 seconds

    const connect = () => {
      if (ws) return;

      console.log('[WS] Connecting to bots WebSocket...');
      ws = new WebSocket('ws://localhost:8000/ws/bots');

      ws.onopen = () => {
        console.log('[WS] Connected successfully');
        setConnectionStatus('connected');
        reconnectAttempts = 0;
      };

      ws.onclose = (e) => {
        console.log('[WS] Disconnected', e);
        setConnectionStatus('disconnected');
        ws = null;
        
        if (reconnectAttempts < maxReconnectAttempts) {
          setTimeout(connect, reconnectDelay);
          reconnectAttempts++;
        }
      };

      ws.onerror = (err) => {
        console.error('[WS] Error:', err);
        setConnectionStatus('error');
      };

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          console.log('[WS] Message received:', msg);

          // Handle different message types
          if (msg.event === 'bot_move') {
            setBots(prev => prev.map(b => 
              b.id === msg.bot_id ? { 
                ...b, 
                x: msg.x, 
                y: msg.y, 
                z: msg.z,
                status: msg.status || b.status,
                path: msg.path || b.path
              } : b
            ));
          }
          else if (msg.event === 'bin_pickup') {
            setBots(prev => prev.map(b => 
              b.id === msg.bot_id ? { ...b, carried_bin_id: msg.bin_id } : b
            ));
          }
          else if (msg.event === 'bin_drop') {
            setDeliveredBins(prev => [...prev, msg.bin_id]);
            setBots(prev => prev.map(b => 
              b.id === msg.bot_id ? { ...b, carried_bin_id: null } : b
            ));
          }
        } catch (err) {
          console.error('[WS] Message parse error:', err);
        }
      };
    };

    connect();

    return () => {
      if (ws) {
        console.log('[WS] Cleaning up connection');
        ws.close();
      }
    };
  }, []);

  // Add debug log for bots state in render
  // console.log('[RENDER] Current bots state:', bots); // Removed to reduce console spam

  // Check if there are ready orders
  // const hasReadyOrders = useMemo(() => orders.some(o => o.status === 'ready'), [orders]);

  // Remove the Bot Controller UI section from the returned JSX
  return (
    <div className="w-full h-[calc(100vh-120px)] flex flex-row items-center justify-center bg-gradient-to-br from-[#0a0a0f] via-[#1a1a2e] to-[#0f0f23] rounded-xl shadow-xl p-6 box-border">
      {/* Connection status indicator */}
      <div style={{ position: 'absolute', top: 18, right: 32, zIndex: 10 }}>
        <span style={{
          display: 'inline-block',
          width: 14,
          height: 14,
          borderRadius: '50%',
          background: connectionStatus === 'connected' ? '#22c55e' : connectionStatus === 'error' ? '#f87171' : '#facc15',
          marginRight: 8,
          border: '2px solid #fff',
          boxShadow: '0 0 4px #0008',
        }} />
        <span style={{ color: '#fff', fontWeight: 600, fontSize: 14 }}>
          {connectionStatus === 'connected' ? 'Live' : connectionStatus === 'error' ? 'Error' : 'Reconnecting...'}
        </span>
      </div>
      {/* Left Panel: Grid Controller */}
      <div className="flex flex-col items-start gap-6 mr-8" style={{ minWidth: 340, maxWidth: 400, width: 340 }}>
        <div className="bg-[#181825] rounded-lg p-8 shadow-md w-full">
          <h2 className="text-lg font-semibold mb-4 text-white">Grid Controller</h2>
          {/* Grid size slider */}
          <div className="mb-4">
            <label className="block text-white mb-1">Grid Size</label>
            <input type="range" min={5} max={12} value={gridSize} onChange={e => setGridSize(Number(e.target.value))} className="w-full" />
            <div className="text-xs text-gray-300 mt-1">{gridSize} x {gridSize}</div>
          </div>
          {/* Grid height slider */}
          <div className="mb-4">
            <label className="block text-white mb-1">Grid Height</label>
            <input type="range" min={3} max={8} value={gridHeight} onChange={e => setGridHeight(Number(e.target.value))} className="w-full" />
            <div className="text-xs text-gray-300 mt-1">{gridHeight} levels</div>
          </div>
          {/* Reset grid button */}
          <button onClick={handleResetGrid} className="w-full bg-[#6366f1] text-white py-2 px-4 rounded mb-2 mt-2 hover:bg-[#4f46e5] transition">Reset Grid</button>
          {/* Force Refresh Bins button */}
          <button
            onClick={handleForceRefreshBins}
            className="w-full bg-[#00bcd4] text-white py-2 px-4 rounded mt-2 hover:bg-[#0097a7] transition"
          >
            Force Refresh Bins
          </button>
          {/* Temporary Test CORS button */}
          <button
            onClick={() => {
              fetch('http://localhost:8000/test-cors')
                .then(res => res.json())
                .then(data => console.log('CORS test result:', data))
                .catch(err => console.error('CORS test error:', err));
            }}
            className="w-full bg-[#f39c12] text-white py-2 px-4 rounded mt-2 hover:bg-[#e67e22] transition"
          >
            Test CORS (Console)
          </button>
        </div>
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
      {/* Right Panel (System Status, Bot Status, etc.) remains unchanged */}
      <div className="ml-8 flex flex-col items-start justify-start min-w-[260px] max-w-[320px]">
        <div className="bg-slate-900 rounded-xl shadow-lg p-6 w-full mb-4">
          <div className="text-lg font-bold text-cyan-300 mb-2">System Status</div>
          <div className="mb-2 text-slate-300">Grid Cells: <span className="font-bold">{totalCells}</span></div>
          <div className="mb-2 text-slate-300">Total Bins: <span className="font-bold">{totalBins}</span></div>
          <div className="mb-2 text-slate-300">Storage Density: <span className="font-bold text-cyan-300">{density}x</span></div>
          <div className="mb-2 text-slate-300">Active Robots: <span className="font-bold">{activeRobots}</span></div>
        </div>
        <div className="bg-slate-900 rounded-xl shadow-lg p-6 w-full">
          <div className="text-lg font-bold text-cyan-300 mb-2">Bot Status</div>
          {bots.map((bot, i) => (
            <div key={bot.id} className="mb-2 px-2 py-1 rounded bg-slate-800 text-slate-200 flex items-center justify-between">
              <span>Robot {bot.id}:</span>
              <span className="ml-2 font-mono text-xs">{bot.status.toUpperCase()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 