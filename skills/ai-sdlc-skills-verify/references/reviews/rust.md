# Rust review guide

Detected by `Cargo.toml` at the repository root. Apply in addition to the acceptance-criteria matrix.

- **Unsafe audit**: every `unsafe` block has a comment stating the invariant it upholds and why it holds; no `unsafe` introduced solely to silence the borrow checker without a documented reason.
- **FFI**: pointers crossing the FFI boundary are checked for null before dereference; ownership of allocated memory across the boundary is documented (who frees it); `#[repr(C)]` used on any struct shared with C.
- **Ownership**: `.clone()` is not used to route around a borrow-checker error the design should instead resolve with lifetimes or restructuring; `Rc`/`Arc` + `RefCell`/`Mutex` used only where shared mutable ownership is genuinely required, not as a default escape hatch.
- **Async patterns**: no blocking calls (`std::thread::sleep`, sync I/O, `Mutex::lock` held across an `.await`) inside an async runtime task; cancellation safety considered for any `select!`/timeout-wrapped future.
- **Error design**: library code returns typed errors (`thiserror`) rather than `anyhow`/`Box<dyn Error>` at public boundaries; `.unwrap()`/`.expect()` on a `Result`/`Option` derived from external input is treated as a defect, not a shortcut.
- **Type system**: newtypes/enums used to make invalid states unrepresentable at trust boundaries, rather than relying on runtime validation alone.
