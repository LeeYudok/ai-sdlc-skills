# Go review guide

Detected by `go.mod` at the repository root. Apply in addition to the acceptance-criteria matrix.

- **Error handling**: errors are checked, not discarded (`_ = err` only with a stated reason); wrapped with `%w` to preserve the chain; sentinel/typed errors compared with `errors.Is`/`errors.As`, not string matching.
- **Concurrency**: every goroutine has a defined lifetime and exit path; shared state is guarded (mutex, channel, or `sync/atomic`); `context.Context` is threaded through and honored for cancellation/timeout; no goroutine leaks on the error path.
- **Injection**: SQL built with parameterized queries or a query builder, never string-concatenated with request input; shell/exec calls avoid `sh -c` with untrusted input.
- **Interfaces**: consumer-defined, kept small; exported API accepts interfaces and returns concrete types where practical.
- **Resource handling**: `defer Close()` immediately after successful open; `io.Reader`/`io.Writer` errors checked; no unbounded goroutine or memory growth under load.
- **Project layout**: package boundaries match the module's stated architecture; no import cycles; internal packages (`internal/`) not reached from outside the module.
