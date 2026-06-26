"use client";
export const dynamic = "force-dynamic";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import nextDynamic from "next/dynamic";
import type maplibregl from "maplibre-gl";
import { getMapProject, saveMapProject } from "@/lib/supabase";
import { exportMapAsPNG } from "@/lib/mapExport";
import { exportFramesAsZip } from "@/lib/exportFrames";
import LayerPanel from "@/components/MapBuilder/LayerPanel";
import PhaseEditor from "@/components/MapBuilder/PhaseEditor";
import TimelineBar from "@/components/MapBuilder/TimelineBar";
import type { MapProject, GeoJSONLayer, Phase } from "@/lib/types";

// MapCanvas must be client-only (no SSR) because MapLibre needs the DOM
const MapCanvas = nextDynamic(() => import("@/components/MapBuilder/MapCanvas"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-950 text-gray-500">
      Loading map...
    </div>
  ),
});

type SidebarTab = "layers" | "phases";

export default function MapBuilderPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const mapRef = useRef<maplibregl.Map | null>(null);
  const saveTimer = useRef<NodeJS.Timeout | null>(null);

  const [project, setProject] = useState<MapProject | null>(null);
  const [layers, setLayers] = useState<GeoJSONLayer[]>([]);
  const [phases, setPhases] = useState<Phase[]>([]);
  const [activePhase, setActivePhase] = useState(0);
  const [sidebarTab, setSidebarTab] = useState<SidebarTab>("layers");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportingFrames, setExportingFrames] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load project
  useEffect(() => {
    if (!id) return;
    getMapProject(id)
      .then((p) => {
        if (!p) { setError("Project not found"); return; }
        setProject(p);
        setLayers(p.geojson_layers ?? []);
        setPhases(p.phases ?? []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  // Debounced save helper
  const scheduleSave = useCallback((data: Partial<MapProject>, delay = 1500) => {
    if (!id) return;
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(async () => {
      setSaving(true);
      try { await saveMapProject(id, data); }
      catch (e) { console.error("Auto-save failed:", e); }
      finally { setSaving(false); }
    }, delay);
  }, [id]);

  const handleLayersChange = useCallback((newLayers: GeoJSONLayer[]) => {
    setLayers(newLayers);
    scheduleSave({ geojson_layers: newLayers });
  }, [scheduleSave]);

  const handlePhasesChange = useCallback((newPhases: Phase[]) => {
    setPhases(newPhases);
    scheduleSave({ phases: newPhases });
  }, [scheduleSave]);

  const handleViewChange = useCallback((center: [number, number], zoom: number) => {
    scheduleSave({ center, zoom }, 2000);
  }, [scheduleSave]);

  const handleExport = async () => {
    if (!mapRef.current) return;
    setExporting(true);
    try {
      const filename = `${project?.title ?? "map"}_${project?.theater ?? ""}.png`
        .replace(/[^a-z0-9_\-\.]/gi, "_")
        .toLowerCase();
      await exportMapAsPNG(mapRef.current, filename, 2);
    } finally {
      setExporting(false);
    }
  };

  const handleExportFrames = async () => {
    if (!mapRef.current || phases.length === 0) return;
    setExportingFrames(true);
    try {
      await exportFramesAsZip(
        mapRef.current,
        phases,
        project?.title ?? "map",
        setActivePhase,
        2,
      );
    } finally {
      setExportingFrames(false);
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

  return (
    <div className="h-screen flex flex-col bg-gray-950">
      {/* Header */}
      <header className="flex items-center gap-4 px-4 py-2 bg-gray-900 border-b border-gray-700 flex-shrink-0">
        <button
          onClick={() => router.push("/maps")}
          className="text-gray-400 hover:text-white text-sm"
        >
          ← Maps
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="text-white font-bold truncate">{project?.title}</h1>
          <p className="text-xs text-gray-500">{project?.theater}</p>
        </div>
        <div className="flex items-center gap-2">
          {saving && <span className="text-xs text-gray-500">Saving...</span>}
          <button
            onClick={handleExport}
            disabled={exporting}
            className="bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white text-sm px-3 py-1.5 rounded-lg transition-colors"
          >
            {exporting ? "Exporting..." : "Export PNG"}
          </button>
        </div>
      </header>

      {/* Body: sidebar + map */}
      <div className="flex flex-1 min-h-0">
        {/* Sidebar */}
        <div className="w-72 flex-shrink-0 flex flex-col overflow-hidden border-r border-gray-700">
          {/* Tab switcher */}
          <div className="flex border-b border-gray-700 flex-shrink-0">
            {(["layers", "phases"] as SidebarTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setSidebarTab(tab)}
                className={`flex-1 py-2 text-xs font-medium capitalize transition-colors ${
                  sidebarTab === tab
                    ? "bg-gray-800 text-white border-b-2 border-blue-500"
                    : "text-gray-500 hover:text-gray-300"
                }`}
              >
                {tab}
                {tab === "phases" && phases.length > 0 && (
                  <span className="ml-1 text-blue-400">({phases.length})</span>
                )}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-hidden">
            {sidebarTab === "layers" ? (
              <LayerPanel
                layers={layers}
                phases={phases}
                activePhase={activePhase}
                onChange={handleLayersChange}
              />
            ) : (
              <PhaseEditor
                phases={phases}
                activePhase={activePhase}
                onPhasesChange={handlePhasesChange}
                onActivePhaseChange={setActivePhase}
              />
            )}
          </div>
        </div>

        {/* Map + Timeline */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 relative">
            <MapCanvas
              layers={layers}
              activePhase={activePhase}
              center={project?.center ?? undefined}
              zoom={project?.zoom ?? 6}
              onMapReady={(m) => { mapRef.current = m; }}
              onViewChange={handleViewChange}
            />
          </div>

          {/* Timeline bar — only shown when there are phases */}
          {phases.length > 0 && (
            <TimelineBar
              phases={phases}
              activePhase={activePhase}
              onPhaseChange={setActivePhase}
              onExportFrames={handleExportFrames}
              exportingFrames={exportingFrames}
            />
          )}
        </div>
      </div>
    </div>
  );
}
