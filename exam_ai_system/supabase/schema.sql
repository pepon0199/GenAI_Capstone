create table if not exists public.exam_attempts (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    topic text not null,
    exam_type text not null,
    level text not null,
    question_count integer not null,
    score integer not null,
    percentage double precision not null,
    provider text not null,
    created_at timestamptz not null default timezone('utc', now())
);

create index if not exists exam_attempts_user_id_created_at_idx
on public.exam_attempts (user_id, created_at desc);
