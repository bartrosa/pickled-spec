Feature: Draft corpus generation from seed examples for differential testing
  As a developer working with pickled-diff
  I want to generate a draft corpus from a small set of seed examples
  So that I can create larger test datasets for differential testing

  Background:
    Given the diff_draft_corpus_from_examples tool is available

  Scenario: Developer generates draft corpus with minimum required parameters
    Given I have a set of seed examples
    And I specify a target size for the corpus
    When I invoke diff_draft_corpus_from_examples with seed_examples and target_size
    Then a draft corpus is produced
    And the corpus contains entries expanded from the seed examples
    And the corpus size matches the specified target size

  Scenario: Developer generates draft corpus with documentation notes
    Given I have a set of seed examples
    And I specify a target size for the corpus
    And I provide notes documenting the corpus generation context
    When I invoke diff_draft_corpus_from_examples with seed_examples, target_size, and notes
    Then a draft corpus is produced
    And the corpus includes the provided notes
    And the corpus size matches the specified target size

  @diff-domain:differential-oracle-gate
  Scenario: Draft corpus output is compatible with run_all gate
    Given I have generated a draft corpus using diff_draft_corpus_from_examples
    When I provide the corpus result to the run_all gate
    Then the run_all gate can consume the corpus
    And the run_all gate can execute differential testing with the corpus

  # TODO: Verify exact format of draft corpus output from source
  # TODO: Verify exact expansion mechanism used to reach target size from seed examples
  Scenario Outline: Developer generates corpora with various target sizes
    Given I have <seed_count> seed examples
    When I invoke diff_draft_corpus_from_examples with target_size of <target_size>
    Then a draft corpus is produced
    And the corpus contains <target_size> entries

    Examples:
      | seed_count | target_size |
      | 5          | 10          |
      | 5          | 50          |
      | 10         | 100         |
      | 3          | 20          |

  Scenario: Tool fails when seed_examples parameter is missing
    Given I specify a target size for the corpus
    When I invoke diff_draft_corpus_from_examples without seed_examples
    Then the tool returns an error indicating seed_examples is required

  Scenario: Tool fails when target_size parameter is missing
    Given I have a set of seed examples
    When I invoke diff_draft_corpus_from_examples without target_size
    Then the tool returns an error indicating target_size is required
