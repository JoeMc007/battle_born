import { createClient } from "@supabase/supabase-js";
import type { MapProject, OOBProject } from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type SupabaseClient = ReturnType<typeof createClient<any>>;
let _client: SupabaseClient | null = null;

function getClient(): SupabaseClient {
  if (!_client) {
    _client = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
    ) as SupabaseClient;
  }
  return _client;
}

// ── Map Projects ──────────────────────────────────────────────────────────────

export async function getMapProjects(): Promise<MapProject[]> {
  const { data, error } = await getClient()
    .from("map_projects")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return data ?? [];
}

export async function getMapProject(id: string): Promise<MapProject | null> {
  const { data, error } = await getClient()
    .from("map_projects")
    .select("*")
    .eq("id", id)
    .single();
  if (error) throw error;
  return data;
}

export async function createMapProject(
  project: Omit<MapProject, "id" | "created_at" | "updated_at">
): Promise<MapProject> {
  const { data, error } = await getClient()
    .from("map_projects")
    .insert({ ...project, updated_at: new Date().toISOString() })
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function saveMapProject(
  id: string,
  updates: Partial<MapProject>
): Promise<MapProject> {
  const { data, error } = await getClient()
    .from("map_projects")
    .update({ ...updates, updated_at: new Date().toISOString() })
    .eq("id", id)
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function deleteMapProject(id: string): Promise<void> {
  const { error } = await getClient().from("map_projects").delete().eq("id", id);
  if (error) throw error;
}

// ── OOB Projects ──────────────────────────────────────────────────────────────

export async function getOOBProjects(): Promise<OOBProject[]> {
  const { data, error } = await getClient()
    .from("oob_projects")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return data ?? [];
}

export async function getOOBProject(id: string): Promise<OOBProject | null> {
  const { data, error } = await getClient()
    .from("oob_projects")
    .select("*")
    .eq("id", id)
    .single();
  if (error) throw error;
  return data;
}

export async function createOOBProject(
  project: Omit<OOBProject, "id" | "created_at" | "updated_at">
): Promise<OOBProject> {
  const { data, error } = await getClient()
    .from("oob_projects")
    .insert({ ...project, updated_at: new Date().toISOString() })
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function saveOOBProject(
  id: string,
  updates: Partial<OOBProject>
): Promise<OOBProject> {
  const { data, error } = await getClient()
    .from("oob_projects")
    .update({ ...updates, updated_at: new Date().toISOString() })
    .eq("id", id)
    .select()
    .single();
  if (error) throw error;
  return data;
}
