"use client";

import { useState } from "react";
import type { Phase } from "@/lib/types";

interface PhaseEditorProps {
  phases: Phase[];
  activePhase: number;
  onPhasesChange: (phases: Phase[]) => void;
  onActivePhaseChange: (index: number) => void;
}

export default function PhaseEditor({
  phases,
  activePhase,
  onPhasesChange,
  onActivePhaseChange,
}: PhaseEditorProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [draft, setDraft] = useState<Partial<Phase>>({});

  function addPhase() {
    const newPhase: Phase = {
      index: phases.length,
      label: `Phase ${phases.length + 1}`,
      date: "",
      description: "",
    };
    const next = [...phases, newPhase];
    onPhasesChange(next);
    onActivePhaseChange(newPhase.index);
    setEditingIndex(newPhase.index);
    setDraft(newPhase);
  }

  function startEdit(p: Phase) {
    setEditingIndex(p.index);
    setDraft({ ...p });
  }

  function commitEdit() {
    if (editingIndex === null) return;
    const next = phases.map((p) =>
      p.index === editingIndex ? { ...p, ...draft } as Phase : p
    );
    onPhasesChange(next);
    setEditingIndex(null);
    setDraft({});
  }

  function deletePhase(index: number) {
    const next = phases
      .filter((p) => p.index !== index)
      .map((p, i) => ({ ...p, index: i }));
    onPhasesChange(next);
    const newActive = Math.min(activePhase, next.length - 1);
    onActivePhaseChange(Math.max(0, newActive));
    setEditingIndex(null);
  }

  function movePhase(index: number, dir: -1 | 1) {
    const swapIdx = index + dir;
    if (swapIdx < 0 || swapIdx >= phases.length) return;
    const next = [...phases];
    [next[index], next[swapIdx]] = [next[swapIdx], next[index]];
    const reindexed = next.map((p, i) => ({ ...p, index: i }));
    onPhasesChange(reindexed);
    if (activePhase === index) onActivePhaseChange(swapIdx);
    else if (activePhase === swapIdx) onActivePhaseChange(index);
  }

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Phases
        </span>
        <button
          onClick={addPhase}
          className="text-xs bg-blue-700 hover:bg-blue-600 px-2 py-1 rounded transition-colors"
        >
          + Add Phase
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {phases.length === 0 && (
          <p className="text-xs text-gray-600 text-center mt-6 px-3">
            No phases yet. Add phases to build a timeline.
          </p>
        )}

        {phases.map((p) => (
          <div key={p.index}>
            {editingIndex === p.index ? (
              <div className="p-3 border-b border-gray-700 bg-gray-800">
                <input
                  className="w-full bg-gray-700 text-white text-xs rounded px-2 py-1 mb-1.5 outline-none"
                  placeholder="Phase label (e.g. D-Day +0)"
                  value={draft.label ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, label: e.target.value }))}
                />
                <input
                  className="w-full bg-gray-700 text-white text-xs rounded px-2 py-1 mb-1.5 outline-none"
                  placeholder="Date (e.g. June 6, 1944)"
                  value={draft.date ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, date: e.target.value }))}
                />
                <textarea
                  className="w-full bg-gray-700 text-white text-xs rounded px-2 py-1 mb-2 outline-none resize-none"
                  rows={2}
                  placeholder="Description (optional)"
                  value={draft.description ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, description: e.target.value }))}
                />
                <div className="flex gap-2">
                  <button
                    onClick={commitEdit}
                    className="flex-1 bg-blue-700 hover:bg-blue-600 text-xs py-1 rounded transition-colors"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => { setEditingIndex(null); setDraft({}); }}
                    className="text-xs text-gray-500 hover:text-gray-300 px-2 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div
                onClick={() => onActivePhaseChange(p.index)}
                className={`flex items-center gap-2 px-3 py-2 border-b border-gray-800 cursor-pointer group transition-colors ${
                  activePhase === p.index
                    ? "bg-blue-900/40 border-l-2 border-l-blue-500"
                    : "hover:bg-gray-800"
                }`}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium truncate">{p.label}</p>
                  {p.date && (
                    <p className="text-xs text-gray-500 truncate">{p.date}</p>
                  )}
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => { e.stopPropagation(); movePhase(p.index, -1); }}
                    className="text-gray-500 hover:text-white text-xs px-1"
                    title="Move up"
                  >↑</button>
                  <button
                    onClick={(e) => { e.stopPropagation(); movePhase(p.index, 1); }}
                    className="text-gray-500 hover:text-white text-xs px-1"
                    title="Move down"
                  >↓</button>
                  <button
                    onClick={(e) => { e.stopPropagation(); startEdit(p); }}
                    className="text-gray-500 hover:text-white text-xs px-1"
                    title="Edit"
                  >✎</button>
                  <button
                    onClick={(e) => { e.stopPropagation(); deletePhase(p.index); }}
                    className="text-gray-500 hover:text-red-400 text-xs px-1"
                    title="Delete"
                  >✕</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
