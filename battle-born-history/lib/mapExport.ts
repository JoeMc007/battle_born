// Client-only — must only be called in browser context
import type maplibregl from "maplibre-gl";

export function exportMapAsPNG(
  map: maplibregl.Map,
  filename = "battle-born-map.png",
  pixelRatio = 1,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const actualRatio = map.getPixelRatio();
    map.setPixelRatio(pixelRatio);
    map.once("render", () => {
      map.getCanvas().toBlob(
        (blob) => {
          map.setPixelRatio(actualRatio);
          if (!blob) return reject(new Error("Failed to create blob"));
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(url);
          resolve();
        },
        "image/png"
      );
      map.triggerRepaint();
    });
    map.triggerRepaint();
  });
}
