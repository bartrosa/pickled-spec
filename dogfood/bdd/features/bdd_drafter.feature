Feature: Draft a Gherkin feature from a user story

  As a developer or agent
  I want to generate a draft Gherkin feature from a natural-language user story
  So that I have a starting artifact for BDD workflow gates

  Background:
    Given the model is configured in pickled.config.yaml
    And the budget cap is configured

  @bdd-domain:draft-output-parses-via-pytest-bdd
  @bdd-domain:gherkin-feature-header-required
  @pickled-internal:core-model-from-config-not-hardcoded
  @best-practices:cli-mcp-surface-parity
  Scenario: Developer drafts a feature from a well-formed story via CLI
    Given a well-formed user story describing password reset behavior
    When the developer runs pickled-bdd draft with that story
    Then the feature text starts with "Feature:"
    And the feature text parses cleanly through the pytest-bdd adapter
    And warnings is an empty list
    And the output includes rationale
    And the output includes model_used
    And the model_used matches the configured model in pickled.config.yaml

  @bdd-domain:draft-output-parses-via-pytest-bdd
  @bdd-domain:gherkin-feature-header-required
  @pickled-internal:core-model-from-config-not-hardcoded
  @best-practices:cli-mcp-surface-parity
  @best-practices:agent-path-first-class
  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Agent drafts a feature from a well-formed story via MCP
    Given a well-formed user story describing data export behavior
    When the agent calls bdd_draft_feature_from_story with that story
    Then the feature text starts with "Feature:"
    And the feature text parses cleanly through the pytest-bdd adapter
    And warnings is an empty list
    And the output JSON contains exactly feature_text, rationale, warnings, and model_used
    And the model_used matches the configured model in pickled.config.yaml

  @bdd-domain:draft-empty-story-deterministic-failure
  @bdd-domain:draft-warnings-field-populated-on-failure
  @best-practices:cli-mcp-surface-parity
  Scenario Outline: Developer submits an empty or whitespace-only story via CLI
    Given a story containing <story_content>
    When the developer runs pickled-bdd draft with that story
    Then either a typed error is raised before the LLM call or warnings is populated
    And the feature text is not a partial unparseable feature

    Examples:
      | story_content    |
      | empty string     |
      | whitespace only  |

  @bdd-domain:draft-empty-story-deterministic-failure
  @bdd-domain:draft-warnings-field-populated-on-failure
  @best-practices:agent-path-first-class
  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: Agent submits an empty or whitespace-only story via MCP
    Given a story containing <story_content>
    When the agent calls bdd_draft_feature_from_story with that story
    Then either a typed error is raised before the LLM call or warnings is populated
    And the feature text is not a partial unparseable feature

    Examples:
      | story_content    |
      | empty string     |
      | whitespace only  |

  @pickled-internal:core-llm-cache-default-on
  @best-practices:cli-mcp-surface-parity
  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer submits identical story twice via CLI
    Given a user story describing login behavior
    When the developer runs pickled-bdd draft with that story
    And the developer runs pickled-bdd draft with the identical story text
    Then exactly one billable LLM call is made
    And the second call returns byte-identical output to the first
    And both calls return the same feature_text, rationale, warnings, and model_used

  @pickled-internal:core-llm-cache-default-on
  @best-practices:agent-path-first-class
  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Agent submits identical story twice via MCP
    Given a user story describing registration behavior
    When the agent calls bdd_draft_feature_from_story with that story
    And the agent calls bdd_draft_feature_from_story with the identical story text
    Then exactly one billable LLM call is made
    And the second call returns byte-identical output to the first
    And both calls return the same feature_text, rationale, warnings, and model_used

  @best-practices:llm-drafter-temperature-zero
  @best-practices:cli-mcp-surface-parity
  Scenario: Developer drafts a feature and temperature is zero
    Given a user story
    When the developer runs pickled-bdd draft with that story
    Then the LLM completion uses temperature 0

  @best-practices:llm-drafter-temperature-zero
  @best-practices:agent-path-first-class
  Scenario: Agent drafts a feature and temperature is zero
    Given a user story
    When the agent calls bdd_draft_feature_from_story with that story
    Then the LLM completion uses temperature 0

  @pickled-internal:mcp-output-fixed-json-shape
  @best-practices:cli-mcp-surface-parity
  Scenario: MCP output contains no extra fields
    Given a user story
    When the agent calls bdd_draft_feature_from_story with that story
    And the underlying provider returns additional metadata fields
    Then the output JSON contains exactly feature_text, rationale, warnings, and model_used
    And no provider metadata leaks into the response

  Scenario: Drafter does not auto-tag scenarios with rule references
    Given a well-formed user story
    When the developer runs pickled-bdd draft with that story
    Then the generated scenarios have no @rule tags
    And the feature_text contains no rule annotations

  # TODO: Determine how to test "exactly one billable call on cache hit" without introspecting cache directory
  @best-practices:cli-mcp-surface-parity
  @best-practices:agent-path-first-class
  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: CLI and MCP produce identical output for the same story
    Given a user story describing account deletion
    When the developer runs pickled-bdd draft with that story via CLI
    And the agent calls bdd_draft_feature_from_story with the identical story via MCP
    Then the feature_text from CLI matches the feature_text from MCP
    And the rationale from CLI matches the rationale from MCP
    And the warnings from CLI match the warnings from MCP
    And the model_used from CLI matches the model_used from MCP
