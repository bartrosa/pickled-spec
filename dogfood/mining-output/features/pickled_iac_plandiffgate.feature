Feature: PlanDiffGate compares Terraform plan JSONs and determines pass/warn/fail verdict

  Background:
    Given a PlanDiffGate instance

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when target is not a dict
    Given the target is an integer 123
    And the context contains a valid base_plan dict
    When the gate runs
    Then the verdict is FAIL
    And the notes indicate the actual type received

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when target is not a dict (string type)
    Given the target is a string "not a dict"
    And the context contains a valid base_plan dict
    When the gate runs
    Then the verdict is FAIL
    And the notes indicate the actual type received

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when context is None
    Given the target is a valid plan dict
    And the context is None
    When the gate runs
    Then the verdict is FAIL
    And the notes indicate missing base_plan

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when context does not contain base_plan key
    Given the target is a valid plan dict
    And the context is an empty dict
    When the gate runs
    Then the verdict is FAIL
    And the notes indicate missing base_plan

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when base_plan in context is not a dict
    Given the target is a valid plan dict
    And the context contains base_plan as a string
    When the gate runs
    Then the verdict is FAIL
    And the notes indicate base_plan is not a dict

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate passes when both plans have empty resource_changes
    Given the target plan has no resource_changes key
    And the base_plan has no resource_changes key
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate passes when both plans have null resource_changes
    Given the target plan has resource_changes set to null
    And the base_plan has resource_changes set to null
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate passes when both plans have empty resource_changes lists
    Given the target plan has an empty resource_changes list
    And the base_plan has an empty resource_changes list
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate includes finding for new resource in head plan with non-empty actions
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions ["create"]
    When the gate runs
    Then the verdict is WARN
    And there is 1 finding
    And the finding for "aws_instance.web" has base_actions tuple ()
    And the finding for "aws_instance.web" has head_actions tuple ("create",)
    And the notes are "1 resource change(s) detected."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate includes finding for resource with different actions between plans
    Given the base_plan has a resource "aws_instance.web" with actions ["update"]
    And the target plan has a resource "aws_instance.web" with actions ["replace"]
    When the gate runs
    Then the verdict is FAIL
    And there is 1 finding
    And the finding for "aws_instance.web" has base_actions tuple ("update",)
    And the finding for "aws_instance.web" has head_actions tuple ("replace",)
    And the notes are "1 resource change(s) detected."

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate ignores resources only in base plan
    Given the base_plan has a resource "aws_instance.old" with actions ["delete"]
    And the target plan has an empty resource_changes list
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when any action is delete
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions ["delete"]
    When the gate runs
    Then the verdict is FAIL
    And there is 1 finding
    And the notes are "1 resource change(s) detected."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when any action is replace
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions ["replace"]
    When the gate runs
    Then the verdict is FAIL
    And there is 1 finding
    And the notes are "1 resource change(s) detected."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario Outline: Gate warns for safe actions
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions ["<action>"]
    When the gate runs
    Then the verdict is WARN
    And there is 1 finding
    And the notes are "1 resource change(s) detected."

    Examples:
      | action  |
      | create  |
      | update  |
      | read    |
      | no-op   |

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate warns when all actions are from safe set
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions ["create", "read", "update"]
    When the gate runs
    Then the verdict is WARN
    And there is 1 finding
    And the notes are "1 resource change(s) detected."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate warns for unknown actions outside safe and destructive sets
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions ["unknown_action"]
    When the gate runs
    Then the verdict is WARN
    And there is 1 finding
    And the notes are "1 resource change(s) detected."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate includes multiple findings with correct count in notes
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions ["create"]
    And the target plan has a resource "aws_s3_bucket.data" with actions ["update"]
    When the gate runs
    Then the verdict is WARN
    And there are 2 findings
    And the notes are "2 resource change(s) detected."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate skips non-dict entries in resource_changes
    Given the base_plan has an empty resource_changes list
    And the target plan resource_changes contains a string entry "invalid"
    And the target plan has a resource "aws_instance.web" with actions ["create"]
    When the gate runs
    Then the verdict is WARN
    And there is 1 finding
    And the finding for "aws_instance.web" exists

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate treats missing change field as empty actions
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with no change field
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate treats null change field as empty actions
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with null change field
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate treats missing actions field as empty list
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with change but no actions
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate treats non-list actions as empty list
    Given the base_plan has an empty resource_changes list
    And the target plan has a resource "aws_instance.web" with actions as string "create"
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate preserves action order in findings tuples
    Given the base_plan has a resource "aws_instance.web" with actions ["read", "update", "create"]
    And the target plan has a resource "aws_instance.web" with actions ["create", "update", "delete"]
    When the gate runs
    Then the verdict is FAIL
    And there is 1 finding
    And the finding for "aws_instance.web" has base_actions tuple ("read", "update", "create")
    And the finding for "aws_instance.web" has head_actions tuple ("create", "update", "delete")

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate does not create finding when resource has same actions in both plans
    Given the base_plan has a resource "aws_instance.web" with actions ["update"]
    And the target plan has a resource "aws_instance.web" with actions ["update"]
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate does not create finding for resource with empty actions in both plans
    Given the base_plan has a resource "aws_instance.web" with actions []
    And the target plan has a resource "aws_instance.web" with actions []
    When the gate runs
    Then the verdict is PASS
    And the findings are empty
    And the notes are "No plan changes between base and head."
