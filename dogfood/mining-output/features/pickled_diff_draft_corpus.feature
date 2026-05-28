Feature: Draft corpus generation from seed examples

  As a developer or test engineer
  I want to generate a larger differential test corpus from seed examples
  So that I can create comprehensive test datasets without manual tedium

  Background:
    Given the pickled-diff CLI is available

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer generates corpus from seeds file with specified target size
    Given a seeds file "seeds.json" containing 3 seed items
    When the developer runs draft-corpus with seeds "seeds.json" and target size 10
    Then the command exits with status 0
    And the output is valid JSON
    And the corpus contains exactly 10 items
    And the corpus includes items derived from the original seeds

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer reads seed data from stdin
    Given seed data is available on stdin containing 2 seed items
    When the developer runs draft-corpus with seeds "-" and target size 8
    Then the command exits with status 0
    And the output is valid JSON
    And the corpus contains exactly 8 items

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer writes corpus to stdout by default
    Given a seeds file "seeds.json" containing 3 seed items
    When the developer runs draft-corpus with seeds "seeds.json" and target size 5 without specifying output
    Then the command exits with status 0
    And the corpus JSON is written to stdout

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer writes corpus to specified output file
    Given a seeds file "seeds.json" containing 3 seed items
    When the developer runs draft-corpus with seeds "seeds.json" and target size 5 and output "corpus.json"
    Then the command exits with status 0
    And the corpus JSON is written to file "corpus.json"
    And the file "corpus.json" contains valid JSON

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer provides notes from stdin
    Given a seeds file "seeds.json" containing 3 seed items
    And notes data is available on stdin
    When the developer runs draft-corpus with seeds "seeds.json", target size 7, and notes "-"
    Then the command exits with status 0
    And the output is valid JSON
    And the corpus contains exactly 7 items

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer provides notes from file
    Given a seeds file "seeds.json" containing 3 seed items
    And a notes file "notes.txt" exists
    When the developer runs draft-corpus with seeds "seeds.json", target size 7, and notes "notes.txt"
    Then the command exits with status 0
    And the output is valid JSON
    And the corpus contains exactly 7 items

  # TODO: Clarify expected behavior - should command return only seeds, error, or duplicate seeds?
  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer requests target size equal to number of seeds
    Given a seeds file "seeds.json" containing 5 seed items
    When the developer runs draft-corpus with seeds "seeds.json" and target size 5
    Then the command exits with status 0
    And the corpus contains exactly 5 items

  # TODO: Clarify expected behavior - should command return subset, error, or all seeds?
  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer requests target size less than number of seeds
    Given a seeds file "seeds.json" containing 10 seed items
    When the developer runs draft-corpus with seeds "seeds.json" and target size 3
    Then the command handles the condition appropriately
    And the command exits with an appropriate status code
