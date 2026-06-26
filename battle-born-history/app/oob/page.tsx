"use client";
export const dynamic = "force-dynamic";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getOOBProjects, createOOBProject, deleteOOBProject } from "@/lib/supabase";
import type { OOBProject } from "@/lib/types";

export default function OOBPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<OOBProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");
  const [operation, setOperation] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    getOOBProjects()
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    if (!title.trim()) return;
    setCreating(true);
    try {
      const p = await createOOBProject({
        title: title.trim(),
        operation: operation.trim(),
        nodes: [],
        edges: [],
      });
      router.push(`/oob/${p.id}`);
    } catch (e) {
      console.error(e);
      alert("Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this OOB project?")) return;
    await deleteOOBProject(id).catch(console.error);
    setProjects((p) => p.filter((proj) => proj.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/" className="text-gray-500 hover:text-white text-sm">← Dashboard</Link>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">Order of Battle</h1>
            <p className="text-gray-400 mt-1">NATO-style unit hierarchy trees for your history videos</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-green-700 hover:bg-green-600 text-white font-medium px-4 py-2 rounded-lg transition-colors"
          >
            + New OOB
          </button>
        </div>

        {loading && <p className="text-gray-500">Loading projects...</p>}

        {!loading && projects.length === 0 && (
          <div className="border border-dashed border-gray-700 rounded-xl p-12 text-center">
            <p className="text-gray-500 mb-4">No OOB projects yet.</p>
            <button
              onClick={() => setShowForm(true)}
              className="text-green-400 hover:text-green-300 underline"
            >
              Create your first order of battle →
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <div
              key={p.id}
              onClick={() => router.push(`/oob/${p.id}`)}
              className="bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-xl p-5 cursor-pointer transition-colors group relative"
            >
              <h2 className="font-semibold text-lg mb-1">{p.title}</h2>
              {p.operation && <p className="text-sm text-green-400 mb-2">{p.operation}</p>}
              <p className="text-xs text-gray-600 mt-3">
                {p.nodes?.length ?? 0} units · {p.edges?.length ?? 0} connections
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

      {showForm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">New OOB Project</h2>
            <div className="space-y-3 mb-6">
              <div>
                <label className="text-xs text-gray-400 block mb-1">Title *</label>
                <input
                  autoFocus
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-green-500"
                  placeholder="e.g. US Army — Normandy June 1944"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 block mb-1">Operation (optional)</label>
                <input
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-green-500"
                  placeholder="e.g. Operation Overlord"
                  value={operation}
                  onChange={(e) => setOperation(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                />
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleCreate}
                disabled={creating || !title.trim()}
                className="flex-1 bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white font-medium py-2 rounded-lg transition-colors"
              >
                {creating ? "Creating..." : "Create"}
              </button>
              <button
                onClick={() => { setShowForm(false); setTitle(""); setOperation(""); }}
                className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
