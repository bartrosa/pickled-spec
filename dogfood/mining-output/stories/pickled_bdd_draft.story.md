# Story: draft

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-bdd
- **Surface id:** pickled_bdd_draft
- **Code depth:** callgraph | **Units read:** 3 | **Unresolved:** 1

## Context

This CLI command is invoked by developers or automation to convert a user story written in Markdown into a Gherkin .feature file. It sits early in the pickled-bdd workflow, before ambiguity checking (AmbiguityGate.run). The caller provides a path to a Markdown file containing a user story and optionally specifies an output path; the command uses an LLM to generate the Gherkin feature text.

## What the target does today

Accepts a required `story_file` parameter—a file path string—and reads the file as UTF-8 text to obtain the user story content.

Accepts an optional `output` parameter—a file path string or None. When `output` is None (the default), prints the drafted Gherkin feature text to stdout. When `output` is provided, writes the feature text to that path as UTF-8 and prints a confirmation message "Wrote {output}" to stderr.

Builds an LLM client by delegating to a factory function that respects the environment variable `PICKLED_BDD_LLM_FACTORY` for test overrides. If the factory cannot build a client (raises ConfigError), converts the error to a ClickException with the same message text, which Click will display as a user-facing error.

Drafts a Gherkin feature by passing the story text through an unresolved template rendering step (the rendered prompt content is not observable from this code) and sending the result to an LLM via `complete_prompt` with a system instruction "You output only Gherkin. No prose, no fences." The LLM's response is stripped of leading and trailing whitespace.

Returns a DraftResult object containing:
- `text`: the stripped Gherkin feature text from the LLM
- `rationale`: the fixed string "LLM-drafted from user story; no post-processing applied."
- `warnings`: an empty tuple

Does NOT validate the returned Gherkin syntax or semantics. Any malformed or ambiguous output from the LLM is passed through unchanged.

Raises a ClickException if the LLM client cannot be constructed due to configuration issues.

File I/O errors (e.g., story_file does not exist, output path is not writable) will propagate as unhandled exceptions (FileNotFoundError, PermissionError, etc.).

## What we want to verify

- When `output` is None, the drafted feature text appears on stdout and nothing is written to disk.
- When `output` is a valid path, the drafted feature text is written to that path as UTF-8 and a message "Wrote {output}" appears on stderr.
- The drafted feature text is the LLM response stripped of leading and trailing whitespace.
- A ConfigError from the LLM client factory is converted to a ClickException with the same error message.
- If `story_file` does not exist or is unreadable, a FileNotFoundError or similar I/O exception is raised.
- The DraftResult contains `rationale` equal to "LLM-drafted from user story; no post-processing applied."
- The DraftResult contains an empty `warnings` tuple.
- The command does not validate the Gherkin syntax of the LLM output.

## Inventory references

- Arguments:
- `story_file` (required): 
- `output` (optional): Write the drafted feature to this path. Defaults to stdout.
- Related gates: AmbiguityGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states the command drafts "a .feature file from a user story (Markdown)" but does not mention that invalid Gherkin may be produced, nor that validation is explicitly deferred. The code shows validation is absent and delegated to a later gate (PR-08/AmbiguityGate).
- Docstring drift: The docstring does not describe the stdout vs. file-write behavior controlled by the `output` parameter, nor the stderr confirmation message when writing to a file.
- Docstring drift: The docstring does not mention the LLM client configuration or the possibility of a ClickException when the client cannot be built.

## Status

draft
