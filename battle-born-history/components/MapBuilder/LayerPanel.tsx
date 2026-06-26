"use client";

import { useState } from "react";
import type { GeoJSONLayer, LayerType, Affiliation } from "@/lib/types";
import { nanoid } from "nanoid";

const LAYER_TYPE_LABELS: Record<LayerType, string> = {
  unit_positions: "Unit Positions",
  front_line:     "Front Line",
  movement_arrow: "Movement Arrow",
  objective:      "Objective",
  boundary:       "Boundary",
  supply_route:   "Supply Route",
  custom:         "Custom",
};

const AFFILIATION_COLORS: Record<Affiliation, string> = {
  allied:  "#3b82f6",
  axis:    "#ef4444",
  neutral: "#a3a3a3",
  unknown: "#f59e0b",
};

interface LayerPanelProps {
  layers: GeoJSONLayer[];
  onChange: (layers: GeoJSONLayer[]) => void;
}

export default function LayerPanel({ layers, onChange }: LayerPanelProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState<LayerType>("unit_positions");
  const [newAffiliation, setNewAffiliation] = useState<Affiliation>("allied");
  const [geojsonError, setGeojsonError] = useState("");
  const [rawGeojson, setRawGeojson] = useState("");

  const toggle = (id: string) => {
    onChange(layers.map((l) => (l.id === id ? { ...l, visible: !l.visible } : l)));
  };

  const remove = (id: string) => {
    onChange(layers.filter((l) => l.id !== id));
  };

  const handleAdd = () => {
    setGeojsonError("");
    let geojson: GeoJSON.FeatureCollection;
    try {
      geojson = JSON.parse(rawGeojson.trim() || '{"type":"FeatureCollection","features":[]}');
      if (geojson.type !== "FeatureCollection") throw new Error("Must be a FeatureCollection");
    } catch (e) {
      setGeojsonError("Invalid GeoJSON. Must be a FeatureCollection.");
      return;
    }

    const layer: GeoJSONLayer = {
      id: nanoid(),
      name: newName || `${LAYER_TYPE_LABELS[newType]} ${layers.length + 1}`,
      type: newType,
      affiliation: newAffiliation,
      color: AFFILIATION_COLORS[newAffiliation],
      visible: true,
      geojson,
    };

    onChange([...layers, layer]);
    setIsAdding(false);
    setNewName("");
    setRawGeojson("");
    setGeojsonError("");
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-100 border-r border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h2 className="font-semibold text-sm tracking-wide uppercase text-gray-300">
          Layers
        </h2>
        <button
          onClick={() => setIsAdding(true)}
          className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-2 py-1 rounded"
        >
          + Add Layer
        </button>
      </div>

      {/* Layer list */}
      <div className="flex-1 overflow-y-auto divide-y divide-gray-800">
        {layers.length === 0 && (
          <p className="text-xs text-gray-500 p-4">
            No layers yet. Add a layer to start placing units and front lines.
          </p>
        )}
        {layers.map((layer) => (
          <div key={layer.id} className="flex items-center gap-2 px-3 py-2 hover:bg-gray-800 group">
            {/* Color dot */}
            <span
              className="w-3 h-3 rounded-full flex-shrink-0 border border-white/20"
              style={{ backgroundColor: layer.color }}
            />
            {/* Visibility toggle */}
            <button
              onClick={() => toggle(layer.id)}
              className={`text-xs flex-shrink-0 w-5 ${layer.visible ? "text-white" : "text-gray-600"}`}
              title={layer.visible ? "Hide" : "Show"}
            >
              {layer.visible ? "●" : "○"}
            </button>
            {/* Name + type */}
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate">{layer.name}</p>
              <p className="text-xs text-gray-500">{LAYER_TYPE_LABELS[layer.type]}</p>
            </div>
            {/* Delete */}
            <button
              onClick={() => remove(layer.id)}
              className="text-gray-600 hover:text-red-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
              title="Delete layer"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* Add layer form */}
      {isAdding && (
        <div className="border-t border-gray-700 p-3 bg-gray-850 space-y-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">New Layer</p>
          <input
            type="text"
            placeholder="Layer name (optional)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="w-full text-sm bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white placeholder-gray-500"
          />
          <select
            value={newType}
            onChange={(e) => setNewType(e.target.value as LayerType)}
            className="w-full text-sm bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white"
          >
            {Object.entries(LAYER_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
          <select
            value={newAffiliation}
            onChange={(e) => setNewAffiliation(e.target.value as Affiliation)}
            className="w-full text-sm bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white"
          >
            <option value="allied">Allied (Blue)</option>
            <option value="axis">Axis (Red)</option>
            <option value="neutral">Neutral (Gray)</option>
            <option value="unknown">Unknown (Amber)</option>
          </select>
          <textarea
            placeholder='Paste GeoJSON FeatureCollection here (or leave blank for empty layer)'
            value={rawGeojson}
            onChange={(e) => setRawGeojson(e.target.value)}
            rows={4}
            className="w-full text-xs font-mono bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white placeholder-gray-500 resize-none"
          />
          {geojsonError && <p className="text-xs text-red-400">{geojsonError}</p>}
          <div className="flex gap-2">
            <button
              onClick={handleAdd}
              className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-xs py-1 rounded"
            >
              Add
            </button>
            <button
              onClick={() => { setIsAdding(false); setGeojsonError(""); }}
              className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-xs py-1 rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
