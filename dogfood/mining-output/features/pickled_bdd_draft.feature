Feature: Draft Gherkin feature from user story
  As a developer using pickled-bdd
  I want to convert a Markdown user story into a Gherkin feature file
  So that I can begin defining executable specifications

  Background:
    Given a valid LLM client can be constructed

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer drafts feature to stdout
    Given a user story file exists at "story.md"
    When the developer runs the draft command with story file "story.md" and no output path
    Then the drafted Gherkin feature text appears on stdout
    And the feature text is the LLM response with leading and trailing whitespace removed
    And no file is written to disk

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Developer drafts feature to a file
    Given a user story file exists at "story.md"
    When the developer runs the draft command with story file "story.md" and output path "feature.feature"
    Then the drafted Gherkin feature text is written to "feature.feature" as UTF-8
    And the confirmation message "Wrote feature.feature" appears on stderr
    And nothing appears on stdout

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer receives draft result metadata
    Given a user story file exists at "story.md"
    When the developer runs the draft command with story file "story.md"
    Then the draft result contains rationale "LLM-drafted from user story; no post-processing applied."
    And the draft result contains an empty warnings tuple

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM client configuration fails
    Given the LLM client factory raises a ConfigError with message "Invalid API key"
    And a user story file exists at "story.md"
    When the developer runs the draft command with story file "story.md"
    Then a ClickException is raised with message "Invalid API key"

  @best-practices:agent-path-first-class
  Scenario: User story file does not exist
    Given no file exists at "missing.md"
    When the developer runs the draft command with story file "missing.md"
    Then a FileNotFoundError is raised

  # TODO: Verify behavior when output path is not writable (PermissionError)
  # TODO: Verify behavior when story_file is readable but not valid UTF-8

  @pickled-internal:core-llm-cache-default-on
  Scenario: Command does not validate LLM output
    Given a user story file exists at "story.md"
    And the LLM returns malformed Gherkin text "This is not valid Gherkin syntax!!!"
    When the developer runs the draft command with story file "story.md"
    Then the drafted feature text is "This is not valid Gherkin syntax!!!"
    And no validation error is raised

  @pickled-internal:core-llm-cache-default-on
  Scenario: LLM output whitespace is normalized
    Given a user story file exists at "story.md"
    And the LLM returns text with leading newlines and trailing spaces
    When the developer runs the draft command with story file "story.md"
    Then the drafted feature text has no leading or trailing whitespace
