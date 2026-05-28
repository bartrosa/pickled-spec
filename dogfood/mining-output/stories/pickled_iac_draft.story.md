# Story: draft

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-iac
- **Surface id:** pickled_iac_draft
- **Code depth:** callgraph | **Units read:** 5 | **Unresolved:** 5

## Context

This CLI command is the primary entry point for generating a Terraform infrastructure module from a natural-language user story. It is invoked by users who want to draft IaC code without manually writing HCL. The command accepts a user story describing desired infrastructure, optionally writes the generated Terraform module to a specified directory, or prints it to stdout. It is designed for interactive use or scripting workflows where infrastructure requirements are expressed in prose and translated into executable Terraform code.

## What the target does today

**Inputs:**
- `user_story` (str, required): A natural-language description of the desired infrastructure. Passed directly to the drafting logic.
- `provider` (str, required): The cloud provider for which to generate Terraform code (e.g., "aws"). No default is enforced by this function; caller must supply.
- `output` (Path | None, optional): File-system path where the generated module should be written. If None, output is printed to stdout.

**LLM client construction:**
The surface constructs an LLM client by first checking the `PICKLED_IAC_LLM_FACTORY` environment variable. If set, it must follow the format `"module:callable"` (e.g., `"mypackage:get_client"`); the function dynamically imports the module and calls the specified attribute to obtain an LLM client. If the variable is not set, the surface falls back to reading `PICKLED_LLM_PROVIDER` (defaulting to "anthropic") and uses `pickled_core.llm.factory.build_client` with configuration loaded from `pickled_core.llm.config.load_config()`. If configuration is invalid or missing, a `click.ClickException` is raised with the underlying `ConfigError` message.

**Module generation process:**
The surface delegates drafting to `IaCDrafter.draft_module`, which:
1. Detects whether `terraform` or `opentofu` (aliased as `tofu`) is available on the system PATH. If neither is found, raises `IaCToolMissingError`.
2. Renders a prompt template (unresolved call) incorporating the user story, provider, and any prior validation error feedback.
3. Calls the LLM (via unresolved `complete_prompt`) with the rendered prompt and a system instruction to output only Terraform HCL without code fences or commentary.
4. Strips any leading/trailing triple-backtick fences from the LLM response if present.
5. Writes the resulting HCL to a temporary directory and runs `terraform validate -json` (or `opentofu validate -json`). The validation logic initializes the directory if needed.
6. If validation fails, extracts diagnostic messages from the JSON output and retries generation up to 3 times, appending the previous error feedback to the prompt.
7. After 3 failed attempts, raises `IaCValidationError` with all collected diagnostics.
8. On success, returns an `IaCArtifact` containing the validated HCL content and the format ("terraform" or "opentofu").

**Outputs:**
- If `output` is provided: Creates the directory (including parents) if it does not exist, writes the artifact content to `main.tf` within that directory, and prints a confirmation message `"Wrote <path>/main.tf"` to stderr.
- If `output` is None: Prints the artifact content (the raw HCL) to stdout.

**Error modes:**
- Raises `click.ClickException` if `PICKLED_IAC_LLM_FACTORY` is malformed (missing colon separator).
- Raises `click.ClickException` wrapping `ConfigError` if LLM configuration cannot be loaded.
- Raises `IaCToolMissingError` if neither Terraform nor OpenTofu is found on PATH.
- Raises `IaCValidationError` if the generated HCL fails validation after 3 attempts, including all accumulated diagnostics.
- May raise file-system exceptions (e.g., permission errors) when creating `output` directory or writing `main.tf`.

**Side effects:**
- Executes external `terraform` or `opentofu` binaries for validation, which may create `.terraform` directories and lock files in temporary directories.
- Writes to the file system if `output` is specified.
- Prints to stderr (confirmation message) or stdout (HCL content) depending on `output` presence.

## What we want to verify

- When `output` is None, the function prints the generated HCL content to stdout and does not create any files.
- When `output` is a valid Path, the function creates the directory (including parents) if it does not exist and writes a file named `main.tf` containing the generated HCL content.
- The function prints a confirmation message to stderr in the form `"Wrote <path>/main.tf"` when `output` is provided.
- If neither `terraform` nor `opentofu` (or `tofu`) is available on PATH, the function raises `IaCToolMissingError`.
- If `PICKLED_IAC_LLM_FACTORY` is set but does not contain a colon separator, the function raises `click.ClickException` with a message indicating the required format.
- If LLM configuration cannot be loaded and `PICKLED_IAC_LLM_FACTORY` is not set, the function raises `click.ClickException` wrapping the underlying `ConfigError`.
- The function retries generation up to 3 times if the generated HCL fails validation.
- If all 3 generation attempts produce invalid HCL, the function raises `IaCValidationError` containing all collected validation diagnostics.
- The validation process runs `terraform validate -json` or `opentofu validate -json` against the generated HCL in a temporary directory.
- The function strips leading and trailing triple-backtick code fences from the LLM response before validation.
- The `provider` parameter is passed to the prompt rendering and influences the generated HCL (e.g., AWS vs. Azure resources).
- The function defaults to "anthropic" as the LLM provider when `PICKLED_LLM_PROVIDER` is not set and `PICKLED_IAC_LLM_FACTORY` is not used.

## Inventory references

- Arguments:
- `user_story` (required): 
- `provider` (optional): 
- `output` (optional): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Draft a Terraform module from a user story" but omits the iterative validation-and-retry behavior: the function validates the generated HCL up to 3 times and incorporates error feedback into subsequent generation attempts.
- Docstring drift: The docstring does not mention the optional `output` parameter or the dual behavior of writing to a file versus printing to stdout.
- Docstring drift: The docstring does not mention the `provider` parameter, which is required and directly influences the generated infrastructure code.
- Docstring drift: The docstring does not describe any of the error conditions (missing IaC tools, invalid LLM configuration, validation failures after retries, or malformed factory environment variable).
- Docstring drift: The docstring does not clarify that both Terraform and OpenTofu are supported, with automatic detection of the available binary.

## Status

draft
