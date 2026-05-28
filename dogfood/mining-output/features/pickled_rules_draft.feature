Feature: Draft YAML rule-set from natural-language brief
  As a developer or compliance engineer
  I want to automatically generate a YAML rule-set document from a natural-language description
  So that I can quickly create structured rules without manual YAML authoring

  @bdd-domain:gherkin-feature-header-required
  Scenario: User reads brief from stdin
    Given the brief content is provided via stdin
    When the draft command is invoked with brief argument "-"
    Then the command reads the brief text from stdin

  @best-practices:agent-path-first-class
  Scenario: User reads brief from a file
    Given a brief file exists at a specified path
    When the draft command is invoked with that file path as the brief argument
    Then the command reads UTF-8 text from that file

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM client configuration is invalid
    Given the PICKLED_RULES_LLM_FACTORY environment variable specifies an invalid configuration
    When the draft command attempts to build the LLM client
    Then the command raises a ClickException containing the configuration error message

  @pickled-internal:core-llm-cache-default-on
  Scenario: Command invokes LLM with prompt containing all metadata
    Given a brief text and metadata fields are provided
    When the command constructs the LLM prompt
    Then the prompt contains the brief text
    And the prompt contains the short_name value
    And the prompt contains the source_id value
    And the prompt contains the applies_to value
    And the prompt contains the active_from value

  @pickled-internal:core-llm-cache-default-on
  Scenario: Command validates generated YAML as a rule set
    Given the LLM returns a YAML response
    When the command processes the response
    Then the command attempts to load the YAML as a rule set

  @pickled-internal:core-llm-cache-default-on
  Scenario: Command checks for forbidden tokens in generated YAML
    Given the LLM returns a YAML response
    When the command validates the response
    Then the command checks the lowercased YAML text for forbidden tokens
    And produces warnings if any forbidden tokens are found

  @pickled-internal:core-llm-cache-default-on
  Scenario: User writes generated YAML to stdout
    Given the output argument is None
    And the LLM returns valid YAML
    When the command completes
    Then the generated YAML is written to stdout

  @pickled-internal:core-llm-cache-default-on
  Scenario: User writes generated YAML to a file
    Given the output argument is a file path
    And the LLM returns valid YAML
    When the command completes
    Then the generated YAML is written to that file with UTF-8 encoding

  @pickled-internal:core-llm-cache-default-on
  Scenario: LLM response contains rationale section
    Given the LLM response contains YAML and a rationale section delimited by a sentinel
    When the command processes the response
    Then each rationale line is written to stderr prefixed with "rationale: "

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Validation warnings are written to stderr
    Given the command detects validation warnings
    When the command processes the warnings
    Then each warning is written to stderr prefixed with "warning: "

  @pickled-internal:core-llm-cache-default-on
  Scenario: Command exits with status 1 when validation warnings are present
    Given the LLM returns YAML that triggers validation warnings
    When the command completes and emits the YAML
    Then the command exits with status 1

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Command exits with status 2 on general exception
    Given a non-ClickException occurs during processing
    When the command handles the exception
    Then the exception message is printed to stderr
    And the command exits with status 2

  Scenario: ClickException is re-raised without transformation
    Given a ClickException is raised during processing
    When the command handles the exception
    Then the ClickException is re-raised without being caught or transformed into SystemExit(2)
