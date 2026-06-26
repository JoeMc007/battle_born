"use client";

import { useState } from "react";
import type { Theater } from "@/lib/types";

const THEATERS: Theater[] = [
  "Europe 1939-40", "Europe 1941-42", "Europe 1943-44", "Europe 1944-45",
  "Pacific 1941-42", "Pacific 1942-43", "Pacific 1943-44", "Pacific 1944-45",
  "North Africa 1940-43",
  "Eastern Front 1941-42", "Eastern Front 1942-43", "Eastern Front 1943-45",
  "Korea 1950-53", "Custom",
];

// Default map center by theater
const THEATER_CENTERS: Record<string, [number, number]> = {
  "Europe 1939-40":       [10.0, 50.5],
  "Europe 1941-42":       [15.0, 50.0],
  "Europe 1943-44":       [7.0, 49.5],
  "Europe 1944-45":       [8.0, 50.0],
  "Pacific 1941-42":      [135.0, 10.0],
  "Pacific 1942-43":      [155.0, -8.0],
  "Pacific 1943-44":      [145.0, 5.0],
  "Pacific 1944-45":      [125.0, 15.0],
  "North Africa 1940-43": [18.0, 30.0],
  "Eastern Front 1941-42":[32.0, 52.0],
  "Eastern Front 1942-43":[38.0, 48.0],
  "Eastern Front 1943-45":[28.0, 50.0],
  "Korea 1950-53":        [127.5, 37.5],
  "Custom":               [0.0, 45.0],
};

interface NewProjectModalProps {
  onConfirm: (title: string, theater: Theater, operation: string) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export default function NewProjectModal({ onConfirm, onCancel, isLoading }: NewProjectModalProps) {
  const [title, setTitle] = useState("");
  const [theater, setTheater] = useState<Theater>("Europe 1944-45");
  const [operation, setOperation] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    onConfirm(title.trim(), theater, operation.trim());
  };

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-md shadow-2xl">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-bold text-white">New Map Project</h2>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Project Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Operation Market Garden"
              required
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Theater
            </label>
            <select
              value={theater}
              onChange={(e) => setTheater(e.target.value as Theater)}
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
            >
              {THEATERS.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Operation Name <span className="text-gray-500">(optional)</span>
            </label>
            <input
              type="text"
              value={operation}
              onChange={(e) => setOperation(e.target.value)}
              placeholder="e.g. Operation Overlord"
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={!title.trim() || isLoading}
              className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium py-2 rounded-lg transition-colors"
            >
              {isLoading ? "Creating..." : "Create Project"}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
