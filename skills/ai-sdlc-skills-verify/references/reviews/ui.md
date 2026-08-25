# User interface review guide

Apply when a change alters what a user sees or operates.

- **Scope**: confirm the change kept existing authentication methods, routes, API calls, guards, and post-login redirect intact. Any of these that moved must appear in the specification as an approved decision.
- **"Modern" needs a reason**: when a current pattern is adopted, record what it improves — accessibility, task completion time, error prevention, trust, performance, or brand consistency. A change justified only by "it looks current" is not verified.
- **Before and after**: compare the current deployed screen against the changed one at the viewports the product supports, and in each meaningful state (empty, loading, error, long content, permission-denied).
- **Operability**: keyboard reachability and visible focus order; labels and error messages programmatically linked to their fields; text contrast; behavior at increased zoom or font size; light and dark appearance; behavior on a slow or failing network.
- **Prod safety**: verification against a production environment stays within the repository's own rules for touching production. Never disable an end-to-end safety guard to make a check pass.
