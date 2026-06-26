"use client";
export const dynamic = "force-dynamic";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import nextDynamic from "next/dynamic";
import { getOOBProject, saveOOBProject } from "@/lib/supabase";
import type { OOBProject, OOBNode, OOBEdge, UnitSize, UnitType, Affiliation } from "@/lib/types";
import NodeEditPanel from "@/components/OOB/NodeEditPanel";
import { nanoid } from "nanoid";

// OOBCanvas must be client-only — React Flow requires the DOM
const OOBCanvas = nextDynamic(() => import("@/components/OOB/OOBCanvas"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-950 text-gray-500">
      Loading canvas...
    </div>
  ),
});

const DEFAULT_NODE: Omit<OOBNode, "id" | "position"> = {
  unit_name: "New Unit",
  unit_size: "division" as UnitSize,
  unit_type: "infantry" as UnitType,
  affiliation: "allied" as Affiliation,
  combat_effective: true,
};

export default function OOBBuilderPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const saveTimer = useRef<NodeJS.Timeout | null>(null);

  const [project, setProject] = useState<OOBProject | null>(null);
  const [nodes, setNodes] = useState<OOBNode[]>([]);
  const [edges, setEdges] = useState<OOBEdge[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canvasWrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    getOOBProject(id)
      .then((p) => {
        if (!p) { setError("Project not found"); return; }
        setProject(p);
        setNodes(p.nodes ?? []);
        setEdges(p.edges ?? []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  const scheduleSave = useCallback((data: Partial<OOBProject>) => {
    if (!id) return;
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(async () => {
      setSaving(true);
      try { await saveOOBProject(id, data); }
      catch (e) { console.error("Auto-save failed:", e); }
      finally { setSaving(false); }
    }, 1500);
  }, [id]);

  const handleNodesChange = useCallback((newNodes: OOBNode[]) => {
    setNodes(newNodes);
    scheduleSave({ nodes: newNodes });
  }, [scheduleSave]);

  const handleEdgesChange = useCallback((newEdges: OOBEdge[]) => {
    setEdges(newEdges);
    scheduleSave({ edges: newEdges });
  }, [scheduleSave]);

  const handleNodeUpdate = useCallback((updated: OOBNode) => {
    const newNodes = nodes.map((n) => n.id === updated.id ? updated : n);
    handleNodesChange(newNodes);
  }, [nodes, handleNodesChange]);

  const handleDeleteSelected = useCallback(() => {
    if (!selectedId) return;
    const newNodes = nodes.filter((n) => n.id !== selectedId);
    const newEdges = edges.filter((e) => e.source !== selectedId && e.target !== selectedId);
    handleNodesChange(newNodes);
    handleEdgesChange(newEdges);
    setSelectedId(null);
  }, [selectedId, nodes, edges, handleNodesChange, handleEdgesChange]);

  const addUnit = useCallback(() => {
    const newNode: OOBNode = {
      ...DEFAULT_NODE,
      id: nanoid(),
      unit_name: `Unit ${nodes.length + 1}`,
      position: { x: 100 + Math.random() * 200, y: 100 + Math.random() * 100 },
    };
    const newNodes = [...nodes, newNode];
    handleNodesChange(newNodes);
    setSelectedId(newNode.id);
  }, [nodes, handleNodesChange]);

  const handleExportPNG = async () => {
    if (!canvasWrapRef.current) return;
    setExporting(true);
    try {
      const html2canvas = (await import("html2canvas")).default;
      const canvas = await html2canvas(canvasWrapRef.current, {
        backgroundColor: "#030712",
        scale: 2,
        useCORS: true,
        logging: false,
      });
      const blob = await new Promise<Blob | null>((res) => canvas.toBlob(res, "image/png"));
      if (!blob) throw new Error("Failed to create blob");
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${project?.title ?? "oob"}_oob.png`
        .replace(/[^a-z0-9_\-\.]/gi, "_")
        .toLowerCase();
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Export failed:", e);
      alert("Export failed. Try zooming out first.");
    } finally {
      setExporting(false);
    }
  };

  if (loading) return (
    <div className="h-screen flex items-center justify-center bg-gray-950 text-gray-400">
      Loading project...
    </div>
  );

  if (error) return (
    <div className="h-screen flex items-center justify-center bg-gray-950 text-red-400">
      {error}
    </div>
  );

  const selectedNode = nodes.find((n) => n.id === selectedId) ?? null;

  return (
    <div className="h-screen flex flex-col bg-gray-950">
      {/* Header */}
      <header className="flex items-center gap-4 px-4 py-2 bg-gray-900 border-b border-gray-700 flex-shrink-0">
        <button onClick={() => router.push("/oob")} className="text-gray-400 hover:text-white text-sm">
          ← OOB
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="text-white font-bold truncate">{project?.title}</h1>
          {project?.operation && (
            <p className="text-xs text-gray-500">{project.operation}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {saving && <span className="text-xs text-gray-500">Saving...</span>}
          <button
            onClick={addUnit}
            className="bg-blue-700 hover:bg-blue-600 text-white text-sm px-3 py-1.5 rounded-lg transition-colors"
          >
            + Add Unit
          </button>
          <button
            onClick={handleExportPNG}
            disabled={exporting}
            className="bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white text-sm px-3 py-1.5 rounded-lg transition-colors"
          >
            {exporting ? "Exporting..." : "Export PNG"}
          </button>
        </div>
      </header>

      {/* Toolbar hint */}
      <div className="flex-shrink-0 bg-gray-900/50 border-b border-gray-800 px-4 py-1">
        <p className="text-xs text-gray-600">
          Drag units to position · Connect units by dragging from the bottom handle to another unit's top handle · Select a unit to edit · Delete key removes selected
        </p>
      </div>

      {/* Body */}
      <div className="flex flex-1 min-h-0">
        <div ref={canvasWrapRef} className="flex-1 relative">
          <OOBCanvas
            nodes={nodes}
            edges={edges}
            selectedId={selectedId}
            onNodesChange={handleNodesChange}
            onEdgesChange={handleEdgesChange}
            onSelect={setSelectedId}
          />
        </div>

        {selectedNode && (
          <NodeEditPanel
            node={selectedNode}
            onChange={handleNodeUpdate}
            onDelete={handleDeleteSelected}
            onClose={() => setSelectedId(null)}
          />
        )}
      </div>
    </div>
  );
}
