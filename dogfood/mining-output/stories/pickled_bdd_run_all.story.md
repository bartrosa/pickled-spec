# Story: run_all

## Metadata

- **Surface kind:** gate
- **Package:** pickled-bdd
- **Surface id:** pickled_bdd_run_all
- **Code depth:** callgraph | **Units read:** 3 | **Unresolved:** 1

## Context

This is a batch validation entry point for BDD/Gherkin feature files. A caller (likely a quality-gate orchestrator or CI/CD pipeline) invokes this to check whether all `.feature` files under a project's `features/` directory can be successfully parsed. It returns a structured list of pass/fail results—one per feature file plus a final ambiguity-check result—without requiring a live LLM connection.

## What the target does today

**Inputs:**
- `workdir`: a filesystem path (string or `Path` object) pointing to a project root directory.

**Returns:**
- A list of `GateResult` objects.

**Directory and file discovery:**
- Resolves `workdir` to an absolute path.
- Searches recursively for files matching `features/**/*.feature` (any `.feature` file under a `features/` subdirectory, at any depth).
- If no matching files are found, returns a single-element list: a `PASS` result with `gate_name="bdd.features"` and notes `"no features/ directory"`.

**Parsing each feature file:**
- For each discovered `.feature` file (processed in sorted order):
  - Attempts to parse it by reading the file's UTF-8 text and parsing the Gherkin syntax.
  - **On success:** appends a `GateResult` with:
    - `gate_name` set to `"bdd.parse.<filename>"` (where `<filename>` is the base name of the feature file).
    - `verdict=Verdict.PASS`.
    - `notes` describing the relative path from `workdir` (exact format depends on the unresolved `path.relative_to` method).
  - **On any exception during parsing:** appends a `GateResult` with:
    - `gate_name` set to `"bdd.parse.<filename>"`.
    - `verdict=Verdict.FAIL`.
    - `notes` containing the exception's string representation.

**Parsing constraints:**
- Empty or whitespace-only files raise `ValueError("Gherkin text is empty")`.
- Files without a `Feature:` declaration raise `ValueError("No Feature found in Gherkin text")`.

**Ambiguity gate:**
- After processing all feature files, unconditionally appends a `GateResult` with:
  - `gate_name="bdd.ambiguity"`.
  - `verdict=Verdict.PASS`.
  - `notes="skipped — set PICKLED_BDD_LLM_FACTORY to enable AmbiguityGate"`.
- This result is **always** a pass; no actual ambiguity analysis is performed.

**Side effects:**
- Reads files from disk (each `.feature` file is read once).
- No writes or state modifications.

**Error propagation:**
- Does **not** raise exceptions for malformed feature files; instead records failures as `FAIL` results in the returned list.
- May raise exceptions if `workdir` resolution or file-system globbing fails (e.g., permission errors, invalid path).

## What we want to verify

- When `workdir` contains no `features/` directory or no `.feature` files, returns a single-element list with `gate_name="bdd.features"`, `verdict=PASS`, and notes indicating no features directory.
- When `workdir` contains at least one `.feature` file, the returned list has one result per feature file plus one ambiguity result.
- For a valid, parseable `.feature` file, the corresponding result has `verdict=PASS` and `gate_name="bdd.parse.<filename>"`.
- For a `.feature` file that is empty or whitespace-only, the corresponding result has `verdict=FAIL` and notes containing `"Gherkin text is empty"`.
- For a `.feature` file with content but no `Feature:` block, the corresponding result has `verdict=FAIL` and notes containing `"No Feature found in Gherkin text"`.
- For any `.feature` file that raises an exception during parsing, the corresponding result has `verdict=FAIL` and notes containing the exception message.
- The returned list always ends with a result having `gate_name="bdd.ambiguity"`, `verdict=PASS`, and notes indicating the ambiguity check is skipped.
- Feature files are processed in sorted order (by path).
- The function does not raise exceptions for individual malformed feature files; all parsing errors are captured in `FAIL` results.

## Inventory references

- Arguments:
- (gate class)
- Related gates: run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "AmbiguityGate skipped without LLM" but does not mention that the function **always** returns a passing ambiguity result, regardless of whether feature files exist or are valid. The code unconditionally appends a `PASS` verdict for `bdd.ambiguity`.
- Docstring drift: The docstring does not describe the return type (`list[GateResult]`), the per-file result structure, or the special case when no features are found.
- Docstring drift: The docstring does not mention that parsing errors are caught and returned as `FAIL` results rather than propagated as exceptions.

## Status

draft
