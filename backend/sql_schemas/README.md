# SQL Schemas

This folder is the **single source of truth** for all database schemas.

Every SQL file that needs to be run against Supabase lives here.
Run them in **numbered order** using the Supabase SQL Editor.

---

## Supabase Project

- **URL:** `https://mrkqtpswtmmyralqrjxa.supabase.co`
- **SQL Editor:** https://supabase.com/dashboard/project/mrkqtpswtmmyralqrjxa/sql/new

---

## Files — Run in This Order

| Order | File | Description |
|-------|------|-------------|
| 1 | `01_init_schema.sql` | Creates all 4 tables + pgvector extension + RPC functions |
| 2 | `02_add_expert_id.sql` | Adds `expert_id` column to 3 tables (links KH data to Expert Persona) |

---

## How to Run

1. Open the Supabase SQL Editor (link above)
2. Copy the contents of file `01_init_schema.sql`
3. Paste into the editor → click **Run**
4. Open a new tab in the editor
5. Copy `02_add_expert_id.sql` → paste → click **Run**

> All statements use `IF NOT EXISTS` / `IF NOT EXISTS` guards — safe to re-run.

---

## Adding New Schemas

When adding a new migration:
1. Name it `NN_description.sql` (next number in sequence)
2. Add it to the table above
3. Always use `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
