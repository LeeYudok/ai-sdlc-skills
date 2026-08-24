# Python review guide

Detected by `pyproject.toml`, `requirements.txt`, or `setup.py`. Apply in addition to the acceptance-criteria matrix.

- **Injection**: SQL via parameterized queries or the ORM's query builder, never f-string/`%`-formatted into raw SQL; shell calls use `subprocess` with a list of args, never `shell=True` with untrusted input; template rendering escapes user input (autoescape on for Jinja2/Django templates).
- **Path traversal**: user-controlled path segments are validated/normalized against an allowed root before file access (`os.path.realpath` + prefix check, or a dedicated safe-join helper).
- **Django/FastAPI/Flask specifics**: Django — `raw()`/`extra()` avoided or parameterized, CSRF middleware not disabled, `DEBUG=False` in any prod-like config; FastAPI — Pydantic models validate all external input, dependency-injected auth on every protected route; Flask — `debug=False` and secret key not hardcoded outside local dev config.
- **Async**: blocking calls (sync DB drivers, `requests`, `time.sleep`) not made inside `async def` without `run_in_executor`/an async-native client; awaited coroutines are actually awaited, not silently dropped.
- **ORM patterns**: N+1 queries checked for list endpoints (`select_related`/`prefetch_related`, SQLAlchemy `joinedload`); mass-assignment guarded (explicit field allowlist, not `**request.json` into a model).
- **Error handling**: broad `except Exception:` does not swallow errors silently; secrets/tokens never logged even at debug level.
