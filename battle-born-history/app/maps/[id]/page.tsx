"use client";
export const dynamic = "force-dynamic";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import nextDynamic from "next/dynamic";
import type maplibregl from "maplibre-gl";
import { getMapProject, saveMapProject } from "@/lib/supabase";
import { exportMapAsPNG } from "@/lib/mapExport";
import LayerPanel from "@/components/MapBuilder/LayerPanel";
import type { MapProject, GeoJSONLayer } from "@/lib/types";

// MapCanvas must be client-only (no SSR) because MapLibre needs the DOM
const MapCanvas = nextDynamic(() => import("@/components/MapBuilder/MapCanvas"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-950 text-gray-500">
      Loading map...
    </div>
  ),
});

export default function MapBuilderPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const mapRef = useRef<maplibregl.Map | null>(null);
  const saveTimer = useRef<NodeJS.Timeout | null>(null);

  const [project, setProject] = useState<MapProject | null>(null);
  const [layers, setLayers] = useState<GeoJSONLayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load project
  useEffect(() => {
    if (!id) return;
    getMapProject(id)
      .then((p) => {
        if (!p) { setError("Project not found"); return; }
        setProject(p);
        setLayers(p.geojson_layers ?? []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  // Auto-save layers with debounce
  const handleLayersChange = useCallback((newLayers: GeoJSONLayer[]) => {
    setLayers(newLayers);
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(async () => {
      if (!id) return;
      setSaving(true);
      try {
        await saveMapProject(id, { geojson_layers: newLayers });
      } catch (e) {
        console.error("Auto-save failed:", e);
      } finally {
        setSaving(false);
      }
    }, 1500);
  }, [id]);

  const handleViewChange = useCallback(
    (center: [number, number], zoom: number) => {
      if (!id) return;
      if (saveTimer.current) clearTimeout(saveTimer.current);
      saveTimer.current = setTimeout(() => {
        saveMapProject(id, { center, zoom }).catch(console.error);
      }, 2000);
    },
    [id]
  );

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
            {exporting ? "Exporting..." : "Export PNG (2×)"}
          </button>
        </div>
      </header>

      {/* Body: Layer panel + Map */}
      <div className="flex flex-1 min-h-0">
        <div className="w-72 flex-shrink-0 overflow-hidden">
          <LayerPanel layers={layers} onChange={handleLayersChange} />
        </div>
        <div className="flex-1 relative">
          <MapCanvas
            layers={layers}
            center={project?.center ?? undefined}
            zoom={project?.zoom ?? 6}
            onMapReady={(m) => { mapRef.current = m; }}
            onViewChange={handleViewChange}
          />
        </div>
      </div>
    </div>
  );
}
