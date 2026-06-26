"use client";

import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import type { OOBNode } from "@/lib/types";

// NATO APP-6 unit size symbols (text approximations)
const SIZE_SYMBOLS: Record<string, string> = {
  army_group:  "XXXX",
  army:        "XXX",
  corps:       "XX",
  division:    "X",
  brigade:     "III",
  regiment:    "II",
  battalion:   "I",
  company:     "●",
  platoon:     "◆",
  section:     "▲",
  squad:       "·",
};

// NATO unit type icons (simplified geometric approximations)
const TYPE_ICONS: Record<string, string> = {
  infantry:     "⌇",   // vertical lines → infantry
  armor:        "◻",   // oval → armor
  artillery:    "●",   // dot in circle → artillery
  airborne:     "∧",   // parachute-ish
  mechanized:   "◻⌇",
  cavalry:      "/",
  engineer:     "≡",
  signal:       "~",
  headquarters: "⊕",
  support:      "+",
  air:          "✈",
  naval:        "⌢",
  custom:       "?",
};

const AFFIL_COLORS = {
  allied:  { border: "#3b82f6", bg: "#1e3a5f", text: "#93c5fd" },
  axis:    { border: "#ef4444", bg: "#5f1e1e", text: "#fca5a5" },
  neutral: { border: "#a3a3a3", bg: "#2a2a2a", text: "#d4d4d4" },
  unknown: { border: "#f59e0b", bg: "#4a3000", text: "#fcd34d" },
};

interface NATOUnitNodeProps {
  data: OOBNode & { selected?: boolean };
  selected?: boolean;
}

function NATOUnitNode({ data, selected }: NATOUnitNodeProps) {
  const colors = AFFIL_COLORS[data.affiliation] ?? AFFIL_COLORS.unknown;
  const sizeSymbol = SIZE_SYMBOLS[data.unit_size] ?? "?";
  const typeIcon = TYPE_ICONS[data.unit_type] ?? "?";
  const isDead = data.combat_effective === false;

  return (
    <div
      className={`relative select-none ${isDead ? "opacity-40 grayscale" : ""}`}
      style={{ minWidth: 120 }}
    >
      {/* Parent connection handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-2 !h-2 !bg-gray-400 !border-gray-600"
      />

      {/* NATO box */}
      <div
        className={`rounded border-2 transition-all ${selected ? "shadow-lg shadow-blue-500/30" : ""}`}
        style={{
          borderColor: selected ? "#60a5fa" : colors.border,
          backgroundColor: colors.bg,
        }}
      >
        {/* Size indicator row */}
        <div
          className="text-center text-xs font-bold tracking-widest py-0.5 border-b"
          style={{ borderColor: colors.border, color: colors.text }}
        >
          {sizeSymbol}
        </div>

        {/* Unit type icon box */}
        <div
          className="flex items-center justify-center text-xl font-bold py-2 px-3"
          style={{ color: colors.text, minHeight: 44 }}
        >
          {typeIcon}
        </div>

        {/* Unit name */}
        <div
          className="text-center text-xs font-semibold px-2 py-1 border-t truncate max-w-[140px]"
          style={{ borderColor: colors.border, color: colors.text }}
          title={data.unit_name}
        >
          {data.unit_name}
        </div>

        {/* Nationality badge */}
        {data.nationality && (
          <div
            className="text-center text-xs text-gray-500 pb-1 truncate"
            style={{ color: colors.text + "99" }}
          >
            {data.nationality}
            {data.commander && ` · ${data.commander}`}
          </div>
        )}

        {/* Strength */}
        {data.strength && (
          <div className="text-center text-xs text-gray-500 pb-1">
            {data.strength}
          </div>
        )}
      </div>

      {/* Child connection handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-2 !h-2 !bg-gray-400 !border-gray-600"
      />
    </div>
  );
}

export default memo(NATOUnitNode);
