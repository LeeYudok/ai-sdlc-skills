# Data change checklist

Apply when a change adds, alters, or reads a persistent structure.

## Identify before designing

- which database instance and schema, and who owns it — a shared cluster may host other services' data;
- every read and write path to the affected tables, including batches, collectors, admin tools, and reports;
- keys, uniqueness, foreign keys, and check constraints already relied on;
- indexes that the new access pattern needs, and indexes the change would invalidate;
- transaction boundaries: what must commit atomically, and what a partial commit would leave behind;
- current row counts and growth rate, because migration duration and lock exposure follow from them;
- NULL and default handling for new columns on existing rows;
- deployment order between the schema step and the code that depends on it.

## Generated schema documentation is evidence, not the database

A generated snapshot (for example a `tbls` output) and a code-derived table list (for example a
`dbdoc`-style inventory) answer different questions: what the database contains, and what the code
believes it contains. Cross-check them, and treat any difference as a finding.

- Record when the snapshot was generated and against which revision; a stale snapshot is not the schema.
- Confirm the live structure directly when a claim blocks the impact gate.
- Read migration history for structures the snapshot and the code disagree about.

## Incompatible changes

Sequence them as expand → coexist → backfill and verify → remove the old path. Never remove the old
structure in the same deployment that introduces the new one. Destructive operations require explicit
user consent immediately before execution.
