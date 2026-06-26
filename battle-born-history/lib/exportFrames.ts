// Client-only — must only be called in browser context
import type maplibregl from "maplibre-gl";
import type { Phase } from "./types";

async function renderFrame(map: maplibregl.Map, pixelRatio: number): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const prev = map.getPixelRatio();
    map.setPixelRatio(pixelRatio);
    map.once("render", () => {
      map.getCanvas().toBlob(
        (blob) => {
          map.setPixelRatio(prev);
          if (!blob) return reject(new Error("Failed to create blob"));
          resolve(blob);
        },
        "image/png"
      );
      map.triggerRepaint();
    });
    map.triggerRepaint();
  });
}

function sanitize(s: string) {
  return s.replace(/[^a-z0-9_\-]/gi, "_").toLowerCase();
}

export async function exportFramesAsZip(
  map: maplibregl.Map,
  phases: Phase[],
  projectTitle: string,
  onPhaseActivate: (index: number) => void,
  pixelRatio = 2,
): Promise<void> {
  // Dynamically import JSZip — avoids SSR issues
  const JSZip = (await import("jszip")).default;
  const zip = new JSZip();
  const folder = zip.folder("frames") ?? zip;

  for (const phase of phases) {
    onPhaseActivate(phase.index);
    // Wait for React to re-render + map to update
    await new Promise<void>((r) => setTimeout(r, 300));

    const blob = await renderFrame(map, pixelRatio);
    const filename = `${String(phase.index + 1).padStart(2, "0")}_${sanitize(phase.label)}.png`;
    folder.file(filename, blob);
  }

  const zipBlob = await zip.generateAsync({ type: "blob" });
  const url = URL.createObjectURL(zipBlob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${sanitize(projectTitle)}_frames.zip`;
  a.click();
  URL.revokeObjectURL(url);
}
