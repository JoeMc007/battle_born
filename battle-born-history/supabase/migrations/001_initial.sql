-- Battle Born History — Initial Schema
-- Run this in your Supabase SQL editor

-- Map Projects
create table if not exists map_projects (
  id          uuid primary key default gen_random_uuid(),
  title       text not null,
  theater     text not null,
  operation   text,
  center      jsonb,              -- [lng, lat]
  zoom        numeric default 6,
  geojson_layers jsonb default '[]'::jsonb,
  phases      jsonb default '[]'::jsonb,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

-- OOB Projects
create table if not exists oob_projects (
  id          uuid primary key default gen_random_uuid(),
  title       text not null,
  operation   text not null default '',
  nodes       jsonb default '[]'::jsonb,
  edges       jsonb default '[]'::jsonb,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

-- Indexes for faster lookups
create index if not exists map_projects_created_at_idx on map_projects(created_at desc);
create index if not exists oob_projects_created_at_idx on oob_projects(created_at desc);

-- Enable Row Level Security (optional — remove if not using auth)
alter table map_projects enable row level security;
alter table oob_projects  enable row level security;

-- Permissive policy (single user / no auth required)
-- Replace with user-scoped policy when you add authentication
create policy "allow all" on map_projects for all using (true) with check (true);
create policy "allow all" on oob_projects  for all using (true) with check (true);
