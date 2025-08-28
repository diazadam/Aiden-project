-- Supabase Schema for Aiden/Jarvis
-- Run these in the Supabase SQL editor to ensure tables exist

-- Task execution logging
create table if not exists tasks(
  id bigserial primary key,
  trace_id text,
  account_id text,
  type text,
  payload jsonb,
  status text default 'queued',
  error text,
  created_at timestamptz default now()
);

-- Conversation history
create table if not exists conversations(
  id bigserial primary key,
  account_id text,
  channel text,
  transcript jsonb,
  last_msg_at timestamptz default now()
);

-- Appointment/booking management  
create table if not exists bookings(
  id bigserial primary key,
  account_id text,
  lead_id text,
  service text,
  start_at timestamptz,
  end_at timestamptz,
  notes text,
  status text default 'booked'
);

-- Knowledge base chunks for RAG
create table if not exists kb_chunks(
  id bigserial primary key,
  account_id text,
  source text,
  tags text[],
  content text,
  created_at timestamptz default now()
);

-- Create indexes for performance
create index if not exists tasks_account_id_idx on tasks(account_id);
create index if not exists tasks_trace_id_idx on tasks(trace_id);
create index if not exists tasks_status_idx on tasks(status);
create index if not exists conversations_account_id_idx on conversations(account_id);
create index if not exists bookings_account_id_idx on bookings(account_id);
create index if not exists kb_chunks_account_id_idx on kb_chunks(account_id);