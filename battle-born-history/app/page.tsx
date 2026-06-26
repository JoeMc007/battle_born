import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <header className="border-b border-gray-800 px-8 py-4 flex items-center gap-4">
        <span className="text-2xl">⚔️</span>
        <h1 className="text-xl font-bold tracking-tight">Battle Born History</h1>
      </header>

      <main className="flex-1 max-w-4xl mx-auto px-8 py-16 w-full">
        <h2 className="text-4xl font-bold mb-2">Video Production Tools</h2>
        <p className="text-gray-400 mb-12">
          Build professional maps and order of battle graphics for your history videos.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link href="/maps" className="group">
            <div className="bg-gray-900 hover:bg-gray-800 border border-gray-700 hover:border-blue-500 rounded-2xl p-6 transition-all h-full">
              <div className="text-4xl mb-4">🗺️</div>
              <h3 className="text-lg font-bold mb-2 group-hover:text-blue-400 transition-colors">
                Map Builder
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Build animated tactical maps with unit positions, front lines, movement arrows,
                and phase-by-phase timelines. Export as PNG frames for video editing.
              </p>
              <div className="mt-4 text-xs text-gray-600">
                MapLibre GL · MapTiler tiles · GeoJSON layers
              </div>
            </div>
          </Link>

          <Link href="/oob" className="group">
            <div className="bg-gray-900 hover:bg-gray-800 border border-gray-700 hover:border-green-500 rounded-2xl p-6 transition-all h-full">
              <div className="text-4xl mb-4">📋</div>
              <h3 className="text-lg font-bold mb-2 group-hover:text-green-400 transition-colors">
                OOB Builder
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Build order of battle trees and TO&amp;E graphics. Drag-and-drop unit hierarchy
                with NATO-style node styling. Export as PNG for overlays.
              </p>
              <div className="mt-4 text-xs text-gray-600">
                React Flow · NATO symbols · Alliance color coding
              </div>
            </div>
          </Link>

          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 opacity-60">
            <div className="text-4xl mb-4">🎬</div>
            <h3 className="text-lg font-bold mb-2">YouTube Creator</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Script generation, research, SEO, ElevenLabs export, and visual prompts.
              Managed via the Python CLI.
            </p>
            <div className="mt-4 text-xs text-gray-600 font-mono">
              python main.py produce &quot;your idea&quot;
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
