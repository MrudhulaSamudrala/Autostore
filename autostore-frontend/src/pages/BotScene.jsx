import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';

// Grid and warehouse dimensions
const GRID_SIZE = 6;
const BOT_RADIUS = 0.25;
const BIN_SIZE = 0.3;
const BOT_HEIGHT = 0.4;
const BIN_OFFSET_Z = 0.6;
const DELIVERY_STATION = [5, 0];

// Helper: create a color for each bot
const botColors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff, 0x00ffff];

export default function BotScene() {
  const mountRef = useRef();
  const [bots, setBots] = useState({}); // {bot_id: {x, y, z, carryingBinId}}
  const [bins, setBins] = useState({}); // {bin_id: {x, y, z, status, attachedToBotId}}
  const [binMeshes, setBinMeshes] = useState({}); // bin_id: mesh
  const [botMeshes, setBotMeshes] = useState({}); // bot_id: mesh
  const sceneRef = useRef();
  const cameraRef = useRef();
  const rendererRef = useRef();
  const animationFrameRef = useRef();
  const wsRef = useRef();

  // --- Initialize Three.js scene ---
  useEffect(() => {
    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;
    // Camera
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
    camera.position.set(GRID_SIZE / 2, -GRID_SIZE * 1.2, GRID_SIZE * 2.5);
    camera.lookAt(GRID_SIZE / 2, GRID_SIZE / 2, 0);
    cameraRef.current = camera;
    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;
    // Grid helper
    const gridHelper = new THREE.GridHelper(GRID_SIZE + 1, GRID_SIZE + 1);
    scene.add(gridHelper);
    // Delivery station platform
    const platformGeo = new THREE.BoxGeometry(1, 1, 0.1);
    const platformMat = new THREE.MeshStandardMaterial({ color: 0x8888ff });
    const platform = new THREE.Mesh(platformGeo, platformMat);
    platform.position.set(DELIVERY_STATION[0], DELIVERY_STATION[1], 0.05);
    scene.add(platform);
    // Light
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(0, 0, 10);
    scene.add(light);
    // Animate
    const animate = () => {
      renderer.render(scene, camera);
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    animate();
    return () => {
      cancelAnimationFrame(animationFrameRef.current);
      renderer.dispose();
      mountRef.current.removeChild(renderer.domElement);
    };
  }, []);

  // --- WebSocket: Listen for bot events ---
  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/bots');
    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.event === 'bot_move') {
        setBots(prev => ({
          ...prev,
          [msg.bot_id]: {
            ...prev[msg.bot_id],
            x: msg.x,
            y: msg.y,
            z: msg.z || 0,
          }
        }));
      } else if (msg.event === 'bin_pick') {
        setBins(prev => ({
          ...prev,
          [msg.bin_id]: {
            ...prev[msg.bin_id],
            status: 'in-use',
            attachedToBotId: msg.bot_id,
          }
        }));
        setBots(prev => ({
          ...prev,
          [msg.bot_id]: {
            ...prev[msg.bot_id],
            carryingBinId: msg.bin_id,
          }
        }));
      } else if (msg.event === 'bin_drop') {
        setBins(prev => ({
          ...prev,
          [msg.bin_id]: {
            ...prev[msg.bin_id],
            status: 'in-use',
            attachedToBotId: null,
            x: DELIVERY_STATION[0],
            y: DELIVERY_STATION[1],
            z: 0.15,
          }
        }));
        setBots(prev => ({
          ...prev,
          [msg.bot_id]: {
            ...prev[msg.bot_id],
            carryingBinId: null,
          }
        }));
      } else if (msg.event === 'bin_return_move') {
        setBins(prev => ({
          ...prev,
          [msg.bin_id]: {
            ...prev[msg.bin_id],
            x: msg.x,
            y: msg.y,
            z: msg.z || 0.15,
            status: 'returning',
            attachedToBotId: null,
          }
        }));
      } else if (msg.event === 'bin_return') {
        setBins(prev => ({
          ...prev,
          [msg.bin_id]: {
            ...prev[msg.bin_id],
            x: msg.x,
            y: msg.y,
            z: msg.z || 0.15,
            status: 'available',
            attachedToBotId: null,
          }
        }));
      } else if (msg.event === 'status_update') {
        if (msg.order_id && msg.order_status) {
          // Optionally update order status in a parent/global state
        }
        if (msg.bin_id && msg.bin_status) {
          setBins(prev => ({
            ...prev,
            [msg.bin_id]: {
              ...prev[msg.bin_id],
              status: msg.bin_status,
            }
          }));
        }
        if (msg.bot_id && msg.bot_status) {
          setBots(prev => ({
            ...prev,
            [msg.bot_id]: {
              ...prev[msg.bot_id],
              status: msg.bot_status,
            }
          }));
        }
      }
    };
    return () => wsRef.current && wsRef.current.close();
  }, []);

  // --- Update Three.js meshes for bots and bins ---
  useEffect(() => {
    const scene = sceneRef.current;
    // Bots
    Object.entries(bots).forEach(([bot_id, bot]) => {
      let mesh = botMeshes[bot_id];
      if (!mesh) {
        const geo = new THREE.CylinderGeometry(BOT_RADIUS, BOT_RADIUS, BOT_HEIGHT, 32);
        const mat = new THREE.MeshStandardMaterial({ color: botColors[bot_id % botColors.length] });
        mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(bot.x, bot.y, BOT_HEIGHT / 2);
        scene.add(mesh);
        setBotMeshes(prev => ({ ...prev, [bot_id]: mesh }));
      } else {
        // Animate movement
        mesh.position.set(bot.x, bot.y, BOT_HEIGHT / 2);
      }
      // If carrying a bin, attach bin mesh
      if (bot.carryingBinId && binMeshes[bot.carryingBinId]) {
        const binMesh = binMeshes[bot.carryingBinId];
        binMesh.position.set(bot.x, bot.y, BOT_HEIGHT / 2 + BIN_OFFSET_Z);
      }
    });
    // Bins
    Object.entries(bins).forEach(([bin_id, bin]) => {
      let mesh = binMeshes[bin_id];
      if (!mesh) {
        const geo = new THREE.BoxGeometry(BIN_SIZE, BIN_SIZE, BIN_SIZE);
        const mat = new THREE.MeshStandardMaterial({ color: 0x964B00 });
        mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(bin.x, bin.y, bin.z || BIN_SIZE / 2);
        scene.add(mesh);
        setBinMeshes(prev => ({ ...prev, [bin_id]: mesh }));
      } else {
        // If not attached to bot, update position
        if (!bin.attachedToBotId) {
          mesh.position.set(bin.x, bin.y, bin.z || BIN_SIZE / 2);
        }
      }
      // Hide bin if attached to bot (handled above)
      mesh.visible = !bin.attachedToBotId;
    });
  }, [bots, bins]);

  return (
    <div ref={mountRef} style={{ width: '100%', height: '600px', border: '1px solid #ccc', margin: 'auto' }}>
      {/* Three.js scene will be rendered here */}
    </div>
  );
} 