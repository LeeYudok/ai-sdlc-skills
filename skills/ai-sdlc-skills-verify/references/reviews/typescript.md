# TypeScript review guide

Detected by `package.json` with a `typescript`/`@types/node` dependency or a `tsconfig.json`. Apply in addition to the acceptance-criteria matrix.

- **Prototype pollution**: deep-merge/assign helpers reject `__proto__`, `constructor`, `prototype` keys when the source is user input; `JSON.parse` output is not merged into shared objects without sanitization.
- **Injection**: SQL/query-builder calls are parameterized (Prisma, Drizzle, Knex `.where()` forms), never raw template-string SQL with request input; `eval`/`new Function`/`child_process.exec` never receive unsanitized input.
- **Node.js**: no synchronous blocking calls (`fs.*Sync`, tight loops) on the request path of a server; environment secrets read via `process.env`, never hardcoded or committed.
- **Next.js**: server components/actions revalidate auth on every request (no client-only gating of privileged data); route handlers validate `params`/`searchParams` before use; `dangerouslySetInnerHTML` only with sanitized content.
- **Nest.js**: DI-scoped providers match their intended lifetime (singleton vs. request-scoped); guards/interceptors applied on every route that needs them, not assumed inherited.
- **Async patterns**: every `Promise` is awaited or explicitly handled (`.catch`, `void` with justification); no unhandled promise rejection on a hot path; `Promise.all` used instead of sequential `await` in a loop when operations are independent.
- **Type safety**: `any`/`as unknown as X` casts are not used to silence a real type error at a trust boundary (API response, user input).
