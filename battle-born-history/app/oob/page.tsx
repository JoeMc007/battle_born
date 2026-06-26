"use client";

import Link from "next/link";

export default function OOBPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center gap-6 p-8">
      <div className="text-6xl">📋</div>
      <h1 className="text-3xl font-bold">OOB Builder</h1>
      <p className="text-gray-400 text-center max-w-md">
        Order of Battle builder is coming in Session 3. It will use React Flow for
        drag-and-drop unit hierarchy trees with NATO-style node styling and PNG export.
      </p>
      <Link href="/" className="text-blue-400 hover:text-blue-300 underline">
        ← Back to Dashboard
      </Link>
    </div>
  );
}
