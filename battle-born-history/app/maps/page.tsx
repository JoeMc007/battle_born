"use client";
export const dynamic = "force-dynamic";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMapProjects, createMapProject, deleteMapProject } from "@/lib/supabase";
import NewProjectModal from "@/components/MapBuilder/NewProjectModal";
import type { MapProject, Theater } from "@/lib/types";

const THEATER_CENTERS: Record<string, [number, number]> = {
  "Europe 1939-40": [10.0, 50.5], "Europe 1941-42": [15.0, 50.0],
  "Europe 1943-44": [7.0, 49.5],  "Europe 1944-45": [8.0, 50.0],
  "Pacific 1941-42": [135.0, 10.0], "Pacific 1942-43": [155.0, -8.0],
  "Pacific 1943-44": [145.0, 5.0],  "Pacific 1944-45": [125.0, 15.0],
  "North Africa 1940-43": [18.0, 30.0],
  "Eastern Front 1941-42": [32.0, 52.0], "Eastern Front 1942-43": [38.0, 48.0],
  "Eastern Front 1943-45": [28.0, 50.0], "Korea 1950-53": [127.5, 37.5],
  "Custom": [0.0, 45.0],
};

export default function MapsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<MapProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    getMapProjects()
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (title: string, theater: Theater, operation: string) => {
    setCreating(true);
    try {
      const project = await createMapProject({
        title,
        theater,
        operation: operation || undefined,
        geojson_layers: [],
        center: THEATER_CENTERS[theater] ?? [0, 45],
        zoom: 6,
        phases: [],
      });
      setShowModal(false);
      router.push(`/maps/${project.id}`);
    } catch (e) {
      console.error(e);
      alert("Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this map project?")) return;
    await deleteMapProject(id).catch(console.error);
    setProjects((p) => p.filter((proj) => proj.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Map Projects</h1>
            <p className="text-gray-400 mt-1">
              Build animated tactical maps for your history videos
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors"
          >
            + New Map Project
          </button>
        </div>

        {loading && (
          <p className="text-gray-500">Loading projects...</p>
        )}

        {!loading && projects.length === 0 && (
          <div className="border border-dashed border-gray-700 rounded-xl p-12 text-center">
            <p className="text-gray-500 mb-4">No map projects yet.</p>
            <button
              onClick={() => setShowModal(true)}
              className="text-blue-400 hover:text-blue-300 underline"
            >
              Create your first map project →
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <div
              key={p.id}
              onClick={() => router.push(`/maps/${p.id}`)}
              className="bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-xl p-5 cursor-pointer transition-colors group relative"
            >
              <h2 className="font-semibold text-lg mb-1">{p.title}</h2>
              {p.operation && (
                <p className="text-sm text-blue-400 mb-2">{p.operation}</p>
              )}
              <p className="text-sm text-gray-500">{p.theater}</p>
              <p className="text-xs text-gray-600 mt-3">
                {p.geojson_layers?.length ?? 0} layers
                {p.phases?.length ? ` · ${p.phases.length} phases` : ""}
              </p>
              <p className="text-xs text-gray-700 mt-1">
                {new Date(p.created_at).toLocaleDateString()}
              </p>
              <button
                onClick={(e) => handleDelete(p.id, e)}
                className="absolute top-3 right-3 text-gray-700 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity text-sm"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>

      {showModal && (
        <NewProjectModal
          onConfirm={handleCreate}
          onCancel={() => setShowModal(false)}
          isLoading={creating}
        />
      )}
    </div>
  );
}
