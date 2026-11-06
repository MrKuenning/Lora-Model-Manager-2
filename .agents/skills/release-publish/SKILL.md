---
name: release-publish
description: >-
  Automates the complete release process for the project: bumps the version in package.json,
  updates CHANGELOG.md with recent changes and current date, runs the frontend production build,
  and commits and pushes to origin/main. Use when the user asks to "publish", "release",
  "ship it", "bump version and publish", or "iterate version".
---

# Release and Publish Skill

Step-by-step workflow for shipping updates:

1. **Version Bump**:
   - Inspect `frontend/package.json`.
   - Increment the patch version (e.g., `2.3.1` -> `2.3.2`) unless a minor or major bump is requested.
   - Update `frontend/package.json` with direct file edits.

2. **Changelog Update**:
   - Check the recent conversation changes, diffs, and commits.
   - Add a new section at the top of `CHANGELOG.md`:
     ```markdown
     ### MM/DD/YYYY - vX.Y.Z

     **Added & Refined**
     - ...

     **Fixed**
     - ...
     ```

3. **Frontend Production Build**:
   - Run `npm.cmd --prefix frontend run build` (`BypassSandbox: true`).
   - Verify that Vite finishes with exit code 0.

4. **Git Commit & Publish**:
   - Stage all files: `git add -A` (`BypassSandbox: true`).
   - Commit: `git commit -m "Release vX.Y.Z: <Summary>"` (`BypassSandbox: true`).
   - Push to remote: `git push origin main` (`BypassSandbox: true`).

5. **Summary**:
   - Provide a concise release confirmation to the user.
