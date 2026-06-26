export type Theater =
  | "Europe 1939-40"
  | "Europe 1941-42"
  | "Europe 1943-44"
  | "Europe 1944-45"
  | "Pacific 1941-42"
  | "Pacific 1942-43"
  | "Pacific 1943-44"
  | "Pacific 1944-45"
  | "North Africa 1940-43"
  | "Eastern Front 1941-42"
  | "Eastern Front 1942-43"
  | "Eastern Front 1943-45"
  | "Korea 1950-53"
  | "Custom";

export type LayerType =
  | "unit_positions"
  | "front_line"
  | "movement_arrow"
  | "objective"
  | "boundary"
  | "supply_route"
  | "custom";

export type Affiliation = "allied" | "axis" | "neutral" | "unknown";

export interface GeoJSONLayer {
  id: string;
  name: string;
  type: LayerType;
  visible: boolean;
  affiliation: Affiliation;
  color: string;
  geojson: GeoJSON.FeatureCollection;
  // Timeline properties (Session 2)
  visible_from?: number; // phase index
  visible_to?: number;   // phase index
}

export interface MapProject {
  id: string;
  title: string;
  theater: Theater;
  operation?: string;
  created_at: string;
  updated_at: string;
  geojson_layers: GeoJSONLayer[];
  center?: [number, number]; // [lng, lat]
  zoom?: number;
  // Timeline (Session 2)
  phases?: Phase[];
}

export interface Phase {
  index: number;
  label: string;       // e.g. "D-Day +0 / June 6"
  date?: string;
  description?: string;
}

// OOB types (Session 3)
export type UnitSize =
  | "army_group" | "army" | "corps" | "division"
  | "regiment" | "brigade" | "battalion" | "company"
  | "platoon" | "section" | "squad";

export type UnitType =
  | "infantry" | "armor" | "artillery" | "airborne"
  | "mechanized" | "cavalry" | "engineer" | "signal"
  | "headquarters" | "support" | "air" | "naval" | "custom";

export interface OOBNode {
  id: string;
  unit_name: string;
  unit_size: UnitSize;
  unit_type: UnitType;
  affiliation: Affiliation;
  nationality?: string;    // "US", "UK", "GER", "SOV" etc.
  commander?: string;
  strength?: string;       // e.g. "~15,000" or "65%"
  notes?: string;
  combat_effective?: boolean; // false = grayed out / destroyed
  position: { x: number; y: number };
}

export interface OOBEdge {
  id: string;
  source: string;
  target: string;
}

export interface OOBProject {
  id: string;
  title: string;
  operation: string;
  created_at: string;
  updated_at: string;
  nodes: OOBNode[];
  edges: OOBEdge[];
}
