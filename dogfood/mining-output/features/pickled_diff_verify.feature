Feature: Differential testing verification command
  As a developer using pickled-diff
  I want to verify a candidate implementation against a trusted oracle
  So that I can detect behavioral differences across a corpus of test inputs

  Background:
    Given the pickled-diff CLI is available
    And a timeout of 30 seconds is configured

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User provides corpus JSON that is not a list
    Given a corpus file "corpus.json" containing a JSON object instead of a list
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then a ClickException is raised with message containing "must be a list"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User provides valid corpus with dictionary entries
    Given a corpus file "corpus.json" containing [{"name": "a", "payload": "b"}]
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then both oracle and candidate commands receive payload "b"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User provides corpus with non-string name and payload
    Given a corpus file "corpus.json" containing [{"name": 1, "payload": 2}]
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the name is coerced to string "1"
    And the payload is coerced to string "2"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User provides corpus with mixed valid and invalid entries
    Given a corpus file "corpus.json" containing [{"name": "x", "payload": "y"}, "not-a-dict", {"name": "z", "payload": "w"}]
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then only the 2 dictionary entries are processed
    And the non-dictionary entry is silently ignored

  # TODO: Verify missing 'name' or 'payload' keys cause KeyError - need corpus structure details
  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User provides corpus with missing required keys
    Given a corpus file "corpus.json" containing [{"name": "x"}]
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then a KeyError is raised

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: User selects comparison strategy
    Given a corpus file "corpus.json" with valid test data
    When the user invokes verify with comparator "<comparator>"
    Then the <strategy> comparator is selected

    Examples:
      | comparator        | strategy          |
      | structural_json   | structural JSON   |
      | exact             | exact equality    |
      | ""                | exact equality    |
      | unrecognized      | exact equality    |

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User provides empty corpus
    Given a corpus file "corpus.json" containing an empty list
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the verdict is PASS
    And the exit code is 0
    And the notes mention "empty"

  @pickled-internal:core-llm-cache-default-on
  Scenario: Oracle fails on every input
    Given a corpus file "corpus.json" with 3 test inputs
    And the oracle command fails for all inputs
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the verdict is FAIL
    And the exit code is 2
    And the notes contain "Oracle failed on every input"

  @pickled-internal:core-llm-cache-default-on
  Scenario: No items successfully compared due to oracle errors
    Given a corpus file "corpus.json" with 2 test inputs
    And the oracle command fails for all inputs
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the verdict is WARN
    And the exit code is 1

  @pickled-internal:core-llm-cache-default-on
  Scenario: Some compared items mismatch
    Given a corpus file "corpus.json" with 4 test inputs
    And 2 inputs produce matching outputs
    And 2 inputs produce mismatched outputs
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the verdict is WARN
    And the exit code is 1

  @pickled-internal:core-llm-cache-default-on
  Scenario: All compared items mismatch
    Given a corpus file "corpus.json" with 3 test inputs
    And all inputs produce mismatched outputs
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the verdict is FAIL
    And the exit code is 2

  @pickled-internal:core-llm-cache-default-on
  Scenario: All items pass comparison
    Given a corpus file "corpus.json" with 5 test inputs
    And all inputs produce matching outputs
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the verdict is PASS
    And the exit code is 0
    And the notes contain "0/5 mismatches"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Verify JSON output structure
    Given a corpus file "corpus.json" with valid test data
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the JSON output contains key "gate"
    And the JSON output contains key "verdict"
    And the JSON output contains key "notes"
    And the JSON output contains key "findings"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Verify finding structure when mismatches occur
    Given a corpus file "corpus.json" with 1 test input
    And the input produces a mismatch
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then each finding contains key "input_repr"
    And each finding contains key "oracle_output"
    And each finding contains key "candidate_output"
    And each finding contains key "diff_summary"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Oracle errors cause items to be skipped from comparison
    Given a corpus file "corpus.json" with 3 test inputs
    And 1 input produces an oracle error
    And 2 inputs produce matching outputs
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then only 2 items are counted as compared
    And the oracle error item is not counted as compared

  @pickled-internal:core-llm-cache-default-on
  Scenario: Candidate errors are counted as mismatches
    Given a corpus file "corpus.json" with 3 test inputs
    And 1 input produces a candidate error
    And 2 inputs produce matching outputs
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then 3 items are counted as compared
    And 1 item is counted as a mismatch
    And a finding is generated for the candidate error

  @core-domain:verdict-three-state-ladder
  Scenario Outline: Exit codes map to verdicts
    Given a corpus file "corpus.json" with test data producing a <verdict> verdict
    When the user invokes verify with oracle "python oracle.py", candidate "python candidate.py", and corpus "corpus.json"
    Then the exit code is <exit_code>

    Examples:
      | verdict | exit_code |
      | PASS    | 0         |
      | WARN    | 1         |
      | FAIL    | 2         |
