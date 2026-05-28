# Story: bdd_draft_feature_from_story

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-bdd
- **Surface id:** bdd_draft_feature_from_story

## Context

BDD practitioners use this tool to quickly generate a first-draft Gherkin feature file by providing a natural-language user story. The tool accelerates the transition from informal requirements to structured, executable specification format, reducing manual boilerplate and helping teams adopt BDD practices more efficiently.

## What the target does today

**bdd_draft_feature_from_story** accepts a required `story_text` argument containing a natural-language user story and returns a drafted Gherkin `.feature` file structure.

The tool produces output that follows Gherkin syntax conventions, typically including Feature, Scenario, and step keywords (Given/When/Then). The draft serves as a starting point that practitioners can refine.

The surface is gated by `AmbiguityGate.run` and `run_all`, meaning the operation will fail if the story text triggers ambiguity detection or other registered gate conditions. The exact nature of these gate checks must be confirmed from source, as the inventory does not document their specific behavior.

## What we want to verify

- Calling the tool with a simple user story string returns a response containing valid Gherkin keywords (Feature, Scenario, Given, When, Then).
- The output can be written to a `.feature` file without syntax errors.
- Providing an empty or whitespace-only `story_text` either returns an error or produces a minimal valid feature template.
- The tool invokes `AmbiguityGate.run` before or during processing (observable via instrumentation or logs).
- Gate failure prevents feature generation and returns an appropriate error message.
- The generated feature content references or incorporates elements from the input `story_text`.
- Multiple invocations with the same `story_text` produce consistent output structure.

## Inventory references

- Arguments:
- `story_text` (required): 
- Related gates: AmbiguityGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
