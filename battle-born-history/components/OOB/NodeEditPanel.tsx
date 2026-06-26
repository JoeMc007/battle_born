"use client";

import type { OOBNode, UnitSize, UnitType, Affiliation } from "@/lib/types";

const UNIT_SIZES: UnitSize[] = [
  "army_group","army","corps","division","brigade",
  "regiment","battalion","company","platoon","section","squad",
];

const UNIT_TYPES: UnitType[] = [
  "infantry","armor","artillery","airborne","mechanized",
  "cavalry","engineer","signal","headquarters","support","air","naval","custom",
];

const SIZE_LABELS: Record<UnitSize, string> = {
  army_group: "Army Group", army: "Army", corps: "Corps", division: "Division",
  brigade: "Brigade", regiment: "Regiment", battalion: "Battalion",
  company: "Company", platoon: "Platoon", section: "Section", squad: "Squad",
};

const TYPE_LABELS: Record<UnitType, string> = {
  infantry: "Infantry", armor: "Armor", artillery: "Artillery",
  airborne: "Airborne", mechanized: "Mechanized", cavalry: "Cavalry",
  engineer: "Engineer", signal: "Signal", headquarters: "HQ",
  support: "Support", air: "Air", naval: "Naval", custom: "Custom",
};

interface NodeEditPanelProps {
  node: OOBNode;
  onChange: (updated: OOBNode) => void;
  onDelete: () => void;
  onClose: () => void;
}

export default function NodeEditPanel({ node, onChange, onDelete, onClose }: NodeEditPanelProps) {
  const set = <K extends keyof OOBNode>(key: K, value: OOBNode[K]) =>
    onChange({ ...node, [key]: value });

  return (
    <div className="w-64 bg-gray-900 border-l border-gray-700 flex flex-col h-full">
      <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between flex-shrink-0">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Edit Unit
        </span>
        <button onClick={onClose} className="text-gray-500 hover:text-white text-sm">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <Field label="Unit Name">
          <input
            className="input"
            value={node.unit_name}
            onChange={(e) => set("unit_name", e.target.value)}
            placeholder="e.g. 1st Infantry Division"
          />
        </Field>

        <Field label="Size">
          <select className="input" value={node.unit_size} onChange={(e) => set("unit_size", e.target.value as UnitSize)}>
            {UNIT_SIZES.map((s) => <option key={s} value={s}>{SIZE_LABELS[s]}</option>)}
          </select>
        </Field>

        <Field label="Type">
          <select className="input" value={node.unit_type} onChange={(e) => set("unit_type", e.target.value as UnitType)}>
            {UNIT_TYPES.map((t) => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
          </select>
        </Field>

        <Field label="Affiliation">
          <select className="input" value={node.affiliation} onChange={(e) => set("affiliation", e.target.value as Affiliation)}>
            <option value="allied">Allied</option>
            <option value="axis">Axis</option>
            <option value="neutral">Neutral</option>
            <option value="unknown">Unknown</option>
          </select>
        </Field>

        <Field label="Nationality">
          <input
            className="input"
            value={node.nationality ?? ""}
            onChange={(e) => set("nationality", e.target.value || undefined)}
            placeholder="e.g. US, UK, GER, SOV"
          />
        </Field>

        <Field label="Commander">
          <input
            className="input"
            value={node.commander ?? ""}
            onChange={(e) => set("commander", e.target.value || undefined)}
            placeholder="e.g. Eisenhower"
          />
        </Field>

        <Field label="Strength">
          <input
            className="input"
            value={node.strength ?? ""}
            onChange={(e) => set("strength", e.target.value || undefined)}
            placeholder="e.g. ~15,000 / 65%"
          />
        </Field>

        <Field label="Notes">
          <textarea
            className="input resize-none"
            rows={2}
            value={node.notes ?? ""}
            onChange={(e) => set("notes", e.target.value || undefined)}
            placeholder="Optional notes"
          />
        </Field>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={node.combat_effective !== false}
            onChange={(e) => set("combat_effective", e.target.checked)}
            className="accent-blue-500"
          />
          <span className="text-xs text-gray-300">Combat Effective</span>
        </label>
      </div>

      <div className="p-3 border-t border-gray-700 flex-shrink-0">
        <button
          onClick={onDelete}
          className="w-full bg-red-900 hover:bg-red-800 text-red-300 text-xs py-1.5 rounded transition-colors"
        >
          Delete Unit
        </button>
      </div>

      <style jsx>{`
        .input {
          width: 100%;
          background: #1f2937;
          border: 1px solid #374151;
          border-radius: 4px;
          padding: 4px 8px;
          color: white;
          font-size: 0.75rem;
          outline: none;
        }
        .input:focus { border-color: #3b82f6; }
      `}</style>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-gray-500">{label}</label>
      {children}
    </div>
  );
}
