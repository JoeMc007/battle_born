"use client";

import { useEffect, useRef, useCallback } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { GeoJSONLayer, Affiliation } from "@/lib/types";

// Affiliation → line/fill color
const AFFILIATION_COLORS: Record<Affiliation, string> = {
  allied: "#3b82f6",   // blue
  axis:   "#ef4444",   // red
  neutral:"#a3a3a3",   // gray
  unknown:"#f59e0b",   // amber
};

interface MapCanvasProps {
  layers: GeoJSONLayer[];
  activePhase?: number;
  center?: [number, number];
  zoom?: number;
  onMapReady?: (map: maplibregl.Map) => void;
  onViewChange?: (center: [number, number], zoom: number) => void;
}

export default function MapCanvas({
  layers,
  activePhase,
  center = [6.0, 50.5], // Default: NW Europe
  zoom = 6,
  onMapReady,
  onViewChange,
}: MapCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const apiKey = process.env.NEXT_PUBLIC_MAPTILER_API_KEY ?? "";

  // Build MapTiler style URL — historical topo with terrain
  const styleUrl = apiKey
    ? `https://api.maptiler.com/maps/topo-v2/style.json?key=${apiKey}`
    : "https://demotiles.maplibre.org/style.json"; // fallback: no key needed

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: styleUrl,
      center,
      zoom,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-right");
    map.addControl(
      new maplibregl.AttributionControl({ compact: true }),
      "bottom-left"
    );

    map.on("load", () => {
      // ── Hillshade terrain layer ───────────────────────────────────────────
      if (apiKey) {
        if (!map.getSource("terrain")) {
          map.addSource("terrain", {
            type: "raster-dem",
            url: `https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=${apiKey}`,
            tileSize: 256,
          });
          map.setTerrain({ source: "terrain", exaggeration: 1.2 });
          map.addLayer({
            id: "hillshade",
            type: "hillshade",
            source: "terrain",
            paint: {
              "hillshade-illumination-anchor": "viewport",
              "hillshade-exaggeration": 0.4,
              "hillshade-shadow-color": "#2d1f0e",
              "hillshade-highlight-color": "#f5f0e8",
            },
          });
        }
      }

      onMapReady?.(map);
    });

    map.on("moveend", () => {
      const c = map.getCenter();
      onViewChange?.([c.lng, c.lat], map.getZoom());
    });

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync layers to map whenever they or the active phase change
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;
    syncLayers(map, layers, activePhase);
  }, [layers, activePhase]);

  return (
    <div ref={containerRef} className="w-full h-full rounded-lg overflow-hidden" />
  );
}

// ── Layer sync ────────────────────────────────────────────────────────────────

function isLayerActiveInPhase(layer: GeoJSONLayer, activePhase: number | undefined): boolean {
  if (activePhase === undefined) return true;
  if (layer.visible_from === undefined && layer.visible_to === undefined) return true;
  const from = layer.visible_from ?? 0;
  const to = layer.visible_to ?? Infinity;
  return activePhase >= from && activePhase <= to;
}

function syncLayers(map: maplibregl.Map, layers: GeoJSONLayer[], activePhase?: number) {
  const activeIds = new Set(layers.map((l) => l.id));

  // Remove layers/sources no longer in list
  const existingLayers = map.getStyle().layers ?? [];
  for (const layer of existingLayers) {
    if (layer.id.startsWith("bbh-") && !activeIds.has(layer.id.replace(/^bbh-/, ""))) {
      if (map.getLayer(layer.id)) map.removeLayer(layer.id);
    }
  }
  const existingSources = Object.keys(map.getStyle().sources ?? {});
  for (const srcId of existingSources) {
    if (srcId.startsWith("bbh-") && !activeIds.has(srcId.replace(/^bbh-/, ""))) {
      if (map.getSource(srcId)) map.removeSource(srcId);
    }
  }

  // Add / update active layers
  for (const layer of layers) {
    const srcId = `bbh-${layer.id}`;
    const color = layer.color || AFFILIATION_COLORS[layer.affiliation] || "#3b82f6";
    const phaseVisible = isLayerActiveInPhase(layer, activePhase);
    const visibility = layer.visible && phaseVisible ? "visible" : "none";

    if (map.getSource(srcId)) {
      (map.getSource(srcId) as maplibregl.GeoJSONSource).setData(layer.geojson);
    } else {
      map.addSource(srcId, { type: "geojson", data: layer.geojson });
    }

    const geomType = getGeomType(layer.geojson);

    if (geomType === "Point" || geomType === "MultiPoint") {
      addOrUpdateLayer(map, {
        id: `bbh-${layer.id}`,
        type: "circle",
        source: srcId,
        layout: { visibility },
        paint: {
          "circle-radius": 7,
          "circle-color": color,
          "circle-stroke-width": 2,
          "circle-stroke-color": "#ffffff",
          "circle-opacity": 0.85,
        },
      });
      // Label
      addOrUpdateLayer(map, {
        id: `bbh-${layer.id}-label`,
        type: "symbol",
        source: srcId,
        layout: {
          visibility,
          "text-field": ["coalesce", ["get", "name"], ["get", "unit"], ""],
          "text-size": 12,
          "text-offset": [0, 1.4],
          "text-anchor": "top",
          "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
        },
        paint: {
          "text-color": "#1a1a1a",
          "text-halo-color": "#ffffff",
          "text-halo-width": 2,
        },
      });
    } else if (geomType === "LineString" || geomType === "MultiLineString") {
      addOrUpdateLayer(map, {
        id: `bbh-${layer.id}`,
        type: "line",
        source: srcId,
        layout: {
          visibility,
          "line-cap": "round",
          "line-join": "round",
        },
        paint: {
          "line-color": color,
          "line-width": layer.type === "front_line" ? 3 : 2,
          "line-dasharray": layer.type === "boundary" ? [4, 3] : [1],
          "line-opacity": 0.9,
        },
      });
    } else if (geomType === "Polygon" || geomType === "MultiPolygon") {
      addOrUpdateLayer(map, {
        id: `bbh-${layer.id}-fill`,
        type: "fill",
        source: srcId,
        layout: { visibility },
        paint: {
          "fill-color": color,
          "fill-opacity": 0.15,
        },
      });
      addOrUpdateLayer(map, {
        id: `bbh-${layer.id}`,
        type: "line",
        source: srcId,
        layout: { visibility },
        paint: {
          "line-color": color,
          "line-width": 2,
          "line-opacity": 0.8,
        },
      });
    }
  }
}

function addOrUpdateLayer(map: maplibregl.Map, layerDef: maplibregl.LayerSpecification) {
  if (map.getLayer(layerDef.id)) {
    // Update visibility
    const vis = (layerDef.layout as Record<string, unknown>)?.visibility;
    if (vis !== undefined) {
      map.setLayoutProperty(layerDef.id, "visibility", vis);
    }
  } else {
    map.addLayer(layerDef);
  }
}

function getGeomType(fc: GeoJSON.FeatureCollection): string {
  const f = fc.features[0];
  if (!f) return "Point";
  return f.geometry?.type ?? "Point";
}

// ── Export helper (called from ExportButton) ─────────────────────────────────
export function exportMapAsPNG(
  map: maplibregl.Map,
  filename = "battle-born-map.png",
  pixelRatio = 2
): Promise<void> {
  return new Promise((resolve, reject) => {
    // Temporarily boost pixel ratio for high-res export
    const canvas = map.getCanvas();
    map.once("render", () => {
      canvas.toBlob(
        (blob) => {
          if (!blob) return reject(new Error("Failed to create blob"));
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(url);
          resolve();
        },
        "image/png"
      );
      map.triggerRepaint();
    });
    map.triggerRepaint();
  });
}
