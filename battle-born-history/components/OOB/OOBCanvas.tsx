"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  type Node,
  type Edge,
  type NodeChange,
  type EdgeChange,
  type Connection,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import NATOUnitNode from "./NATOUnitNode";
import type { OOBNode, OOBEdge } from "@/lib/types";

const NODE_TYPES = { natoUnit: NATOUnitNode };

interface OOBCanvasProps {
  nodes: OOBNode[];
  edges: OOBEdge[];
  selectedId: string | null;
  onNodesChange: (nodes: OOBNode[]) => void;
  onEdgesChange: (edges: OOBEdge[]) => void;
  onSelect: (id: string | null) => void;
}

function oobToFlow(nodes: OOBNode[]): Node[] {
  return nodes.map((n) => ({
    id: n.id,
    type: "natoUnit",
    position: n.position,
    data: n as unknown as Record<string, unknown>,
    selected: false,
  }));
}

function oobEdgesToFlow(edges: OOBEdge[]): Edge[] {
  return edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    type: "smoothstep",
    style: { stroke: "#4b5563", strokeWidth: 2 },
    markerEnd: undefined,
  }));
}

export default function OOBCanvas({
  nodes,
  edges,
  selectedId,
  onNodesChange,
  onEdgesChange,
  onSelect,
}: OOBCanvasProps) {
  const flowNodes = useMemo(() =>
    oobToFlow(nodes).map((n) => ({ ...n, selected: n.id === selectedId })),
  [nodes, selectedId]);

  const flowEdges = useMemo(() => oobEdgesToFlow(edges), [edges]);

  const handleNodesChange = useCallback((changes: NodeChange[]) => {
    const updated = applyNodeChanges(changes, flowNodes);
    onNodesChange(
      updated.map((fn) => ({
        ...(fn.data as unknown as OOBNode),
        position: fn.position,
      }))
    );
  }, [flowNodes, onNodesChange]);

  const handleEdgesChange = useCallback((changes: EdgeChange[]) => {
    const updated = applyEdgeChanges(changes, flowEdges);
    onEdgesChange(updated.map((e) => ({ id: e.id, source: e.source, target: e.target })));
  }, [flowEdges, onEdgesChange]);

  const handleConnect = useCallback((connection: Connection) => {
    const newEdge = addEdge(
      { ...connection, id: `e-${connection.source}-${connection.target}`, type: "smoothstep" },
      flowEdges
    );
    onEdgesChange(newEdge.map((e) => ({ id: e.id, source: e.source, target: e.target })));
  }, [flowEdges, onEdgesChange]);

  const handleSelectionChange = useCallback(
    ({ nodes: sel }: { nodes: Node[]; edges: Edge[] }) => {
      onSelect(sel.length === 1 ? sel[0].id : null);
    },
    [onSelect]
  );

  return (
    <div className="w-full h-full bg-gray-950">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={NODE_TYPES}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={handleConnect}
        onSelectionChange={handleSelectionChange}
        onPaneClick={() => onSelect(null)}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        deleteKeyCode="Delete"
        multiSelectionKeyCode="Shift"
      >
        <Background variant={BackgroundVariant.Dots} color="#374151" gap={24} size={1} />
        <Controls className="!bg-gray-800 !border-gray-700 [&_button]:!bg-gray-800 [&_button]:!border-gray-700 [&_button]:!text-gray-300" />
        <MiniMap
          className="!bg-gray-900 !border-gray-700"
          nodeColor={(n) => {
            const d = n.data as unknown as OOBNode;
            const colors = { allied: "#3b82f6", axis: "#ef4444", neutral: "#a3a3a3", unknown: "#f59e0b" };
            return colors[d.affiliation] ?? "#6b7280";
          }}
          maskColor="rgba(0,0,0,0.6)"
        />
      </ReactFlow>
    </div>
  );
}
