"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { Phase } from "@/lib/types";

interface TimelineBarProps {
  phases: Phase[];
  activePhase: number;
  onPhaseChange: (index: number) => void;
  onExportFrames: () => Promise<void>;
  exportingFrames: boolean;
}

const PLAY_INTERVAL_MS = 2000;

export default function TimelineBar({
  phases,
  activePhase,
  onPhaseChange,
  onExportFrames,
  exportingFrames,
}: TimelineBarProps) {
  const [playing, setPlaying] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const stopPlay = useCallback(() => {
    setPlaying(false);
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
  }, []);

  const startPlay = useCallback(() => {
    if (phases.length < 2) return;
    setPlaying(true);
  }, [phases.length]);

  // Self-advancing playback via activePhase ref
  const activeRef = useRef(activePhase);
  activeRef.current = activePhase;

  useEffect(() => {
    if (!playing) return;
    timerRef.current = setInterval(() => {
      const next = activeRef.current + 1;
      if (next >= phases.length) {
        stopPlay();
      } else {
        onPhaseChange(next);
      }
    }, PLAY_INTERVAL_MS);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [playing, phases.length, onPhaseChange, stopPlay]);

  // Keyboard navigation
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        onPhaseChange(Math.min(activePhase + 1, phases.length - 1));
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        onPhaseChange(Math.max(activePhase - 1, 0));
      } else if (e.key === " ") {
        e.preventDefault();
        playing ? stopPlay() : startPlay();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [activePhase, phases.length, playing, startPlay, stopPlay, onPhaseChange]);

  if (phases.length === 0) return null;

  const current = phases[activePhase];

  return (
    <div className="flex-shrink-0 bg-gray-900 border-t border-gray-700 px-4 py-2">
      {/* Phase label */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <button
            onClick={() => playing ? stopPlay() : startPlay()}
            disabled={phases.length < 2}
            className="w-7 h-7 rounded-full bg-blue-700 hover:bg-blue-600 disabled:opacity-40 flex items-center justify-center transition-colors text-sm"
            title={playing ? "Pause (Space)" : "Play (Space)"}
          >
            {playing ? "⏸" : "▶"}
          </button>
          <div>
            <span className="text-white text-sm font-semibold">{current?.label}</span>
            {current?.date && (
              <span className="text-gray-500 text-xs ml-2">{current.date}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-600">
            {activePhase + 1} / {phases.length}
          </span>
          <button
            onClick={onExportFrames}
            disabled={exportingFrames || phases.length === 0}
            className="bg-green-800 hover:bg-green-700 disabled:opacity-40 text-white text-xs px-3 py-1 rounded-lg transition-colors"
            title="Export one PNG frame per phase at 2x resolution as a ZIP"
          >
            {exportingFrames ? "Exporting..." : "Export Frames ZIP"}
          </button>
        </div>
      </div>

      {/* Scrubber */}
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPhaseChange(Math.max(activePhase - 1, 0))}
          disabled={activePhase === 0}
          className="text-gray-500 hover:text-white disabled:opacity-30 text-xs px-1"
        >◀</button>

        <div className="flex-1 flex gap-1 overflow-x-auto">
          {phases.map((p) => (
            <button
              key={p.index}
              onClick={() => { stopPlay(); onPhaseChange(p.index); }}
              className={`flex-shrink-0 px-2 py-1 rounded text-xs transition-colors whitespace-nowrap ${
                activePhase === p.index
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => onPhaseChange(Math.min(activePhase + 1, phases.length - 1))}
          disabled={activePhase === phases.length - 1}
          className="text-gray-500 hover:text-white disabled:opacity-30 text-xs px-1"
        >▶</button>
      </div>

      {current?.description && (
        <p className="text-xs text-gray-500 mt-1.5 truncate">{current.description}</p>
      )}

      <p className="text-xs text-gray-700 mt-1">← → arrow keys to step · Space to play</p>
    </div>
  );
}
