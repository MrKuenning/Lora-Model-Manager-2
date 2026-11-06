# Project Guidelines & Release Automation

## Shorthand Release Triggers
Whenever the user uses any of the following shorthand phrases:
- `publish`
- `release`
- `ship it`
- `bump and publish`
- `iterate version and publish`

Immediately execute the **Release & Publish Workflow**:
1. **Version Bump**:
   - Read `frontend/package.json` to get the current version.
   - Increment the patch version (e.g. `2.3.1` -> `2.3.2`) unless the user specified a major or minor bump.
   - Update `frontend/package.json` with the new version.
2. **Changelog Update**:
   - Review recent unreleased changes from the conversation/diff.
   - Prepend a new release section to `CHANGELOG.md` with today's date (format: `### MM/DD/YYYY - vX.Y.Z`) detailing:
     - New features / enhancements
     - Bug fixes & UX refinements
3. **Build Frontend**:
   - Run `npm.cmd --prefix frontend run build` (`BypassSandbox: true`).
4. **Git Commit & Publish**:
   - Stage all changes: `git add -A` (`BypassSandbox: true`).
   - Commit: `git commit -m "Release vX.Y.Z: <Summary of changes>"` (`BypassSandbox: true`).
   - Push to GitHub remote: `git push origin main` (`BypassSandbox: true`).
5. **Confirmation**:
   - Provide a clear, concise bulleted summary of the published release and new version.
