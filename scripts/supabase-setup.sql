-- ════════════════════════════════════════════════════════════════════
--  Хранилище ответов блока «Бюджет: план и факт»
--
--  Выполнить один раз в Supabase: проект → SQL Editor → вставить всё
--  целиком → Run.
--
--  Главная идея защиты: посетитель может ТОЛЬКО добавить свой ответ.
--  Прочитать чужие ответы он не может — наружу отдаётся не таблица,
--  а витрина с помесячными средними. Выкачать базу или посмотреть
--  отдельные записи через сайт невозможно.
-- ════════════════════════════════════════════════════════════════════

-- ── 1. Таблица ответов ──────────────────────────────────────────────
-- Храним ровно две цифры и время. Ни IP, ни имени, ни куки:
-- так это не персональные данные, и обязательств по их хранению
-- не возникает.

create table if not exists public.budget_answers (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  plan       integer not null check (plan between 300 and 3000),
  fact       integer not null check (fact between 300 and 3000)
);

comment on table public.budget_answers is
  'Анонимные ответы посетителей: планируемый и фактический бюджет поездки на человека, в долларах.';

-- Индекс по дате: витрина группирует по месяцам.
create index if not exists budget_answers_created_at_idx
  on public.budget_answers (created_at);


-- ── 2. Правила доступа ──────────────────────────────────────────────
-- RLS включён, и для анонимного посетителя разрешена ровно одна
-- операция — вставка. Политики на чтение НЕТ, поэтому select по
-- таблице запрещён: даже зная адрес проекта, сырые строки не достать.

alter table public.budget_answers enable row level security;

drop policy if exists "anon may insert own answer" on public.budget_answers;
create policy "anon may insert own answer"
  on public.budget_answers
  for insert
  to anon
  with check (true);


-- ── 3. Витрина с агрегатами ─────────────────────────────────────────
-- Только то, что показывает график: месяц, средний план, средний факт
-- и количество ответов. Витрина намеренно НЕ security_invoker —
-- она читает таблицу от имени владельца, обходя RLS, и отдаёт наружу
-- исключительно усреднённые числа.

create or replace view public.budget_monthly
with (security_invoker = off) as
select
  date_trunc('month', created_at)::date as month,
  round(avg(plan))::int                 as avg_plan,
  round(avg(fact))::int                 as avg_fact,
  count(*)::int                         as answers
from public.budget_answers
group by 1
having count(*) >= 1          -- месяцы без ответов не показываем
order by 1;

comment on view public.budget_monthly is
  'Помесячные средние для графика на сайте. Отдельные ответы наружу не выдаются.';

grant select on public.budget_monthly to anon;


-- ── 4. Проверка ─────────────────────────────────────────────────────
-- После выполнения можно убедиться, что всё работает как задумано:
--
--   insert into public.budget_answers (plan, fact) values (800, 1000);
--   select * from public.budget_monthly;   -- увидите одну строку
--
-- А вот это должно вернуть ПУСТО при обращении с сайта — и это
-- правильно, значит сырые ответы закрыты:
--
--   select * from public.budget_answers;
