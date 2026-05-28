Feature: Terraform plan diff comparison
  As a DevOps engineer
  I want to compare two Terraform plan JSON files
  So that I can identify infrastructure changes between baseline and proposed plans

  Background:
    Given a CLI command "diff"

  @pickled-internal:core-llm-cache-default-on
  Scenario: Operator compares two identical plans
    Given a valid Terraform plan file at "base.json" with no resource changes
    And a valid Terraform plan file at "head.json" with no resource changes
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 0
    And the output contains valid JSON
    And the verdict is "PASS"
    And the findings array is empty

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares two empty plans
    Given a valid Terraform plan file at "base.json" with resource_changes set to null
    And a valid Terraform plan file at "head.json" with resource_changes set to null
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 0
    And the verdict is "PASS"
    And the findings array is empty

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans where head contains a new resource
    Given a valid Terraform plan file at "base.json" with no resource changes
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "create"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 1
    And the verdict is "WARN"
    And the findings contain a resource "aws_instance.web" with actions_before empty and actions_after "create"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans where head deletes a resource
    Given a valid Terraform plan file at "base.json" with a resource "aws_instance.web" having actions "no-op"
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "delete"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 2
    And the verdict is "FAIL"
    And the findings contain a resource "aws_instance.web" with actions_before "no-op" and actions_after "delete"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans where head replaces a resource
    Given a valid Terraform plan file at "base.json" with a resource "aws_instance.web" having actions "no-op"
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "delete,create"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 2
    And the verdict is "FAIL"
    And the findings contain a resource "aws_instance.web" with actions_before "no-op" and actions_after "delete,create"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans with different actions for same resource
    Given a valid Terraform plan file at "base.json" with a resource "aws_instance.web" having actions "no-op"
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "update"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 1
    And the verdict is "WARN"
    And the findings contain a resource "aws_instance.web" with actions_before "no-op" and actions_after "update"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans where base contains resource not in head
    Given a valid Terraform plan file at "base.json" with a resource "aws_instance.old" having actions "no-op"
    And a valid Terraform plan file at "head.json" with no resource changes
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 0
    And the verdict is "PASS"
    And the findings array is empty

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: Operator compares plans with safe actions only
    Given a valid Terraform plan file at "base.json" with no resource changes
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "<action>"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 1
    And the verdict is "WARN"

    Examples:
      | action  |
      | create  |
      | update  |
      | read    |
      | no-op   |

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator provides non-existent base file
    Given a file "head.json" exists
    And a file "nonexistent.json" does not exist
    When the operator runs diff with base "nonexistent.json" and head "head.json"
    Then the command raises a file not found exception

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator provides non-existent head file
    Given a file "base.json" exists
    And a file "nonexistent.json" does not exist
    When the operator runs diff with base "base.json" and head "nonexistent.json"
    Then the command raises a file not found exception

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator provides file with invalid JSON in base
    Given a file "base.json" contains invalid JSON
    And a valid Terraform plan file at "head.json" with no resource changes
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command raises a JSON decode exception

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator provides file with invalid JSON in head
    Given a valid Terraform plan file at "base.json" with no resource changes
    And a file "head.json" contains invalid JSON
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command raises a JSON decode exception

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator provides head file that is not a dictionary
    Given a valid Terraform plan file at "base.json" with no resource changes
    And a file "head.json" contains a JSON array
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 2
    And the verdict is "FAIL"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator provides base file that is not a dictionary
    Given a file "base.json" contains a JSON array
    And a valid Terraform plan file at "head.json" with no resource changes
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 2
    And the verdict is "FAIL"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans with non-dictionary resource change entries
    Given a valid Terraform plan file at "base.json" with resource_changes containing non-dictionary entries
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "create"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 1
    And the verdict is "WARN"
    And the non-dictionary entries are silently ignored

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans with missing change field
    Given a valid Terraform plan file at "base.json" with a resource "aws_instance.web" missing change field
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "create"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 1
    And the verdict is "WARN"
    And the resource with missing change field is treated as having no actions

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans with non-list actions field
    Given a valid Terraform plan file at "base.json" with a resource "aws_instance.web" having non-list actions
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "update"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 1
    And the verdict is "WARN"
    And the resource with non-list actions is treated as having no actions

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator compares plans with missing address field
    Given a valid Terraform plan file at "base.json" with a resource missing address field
    And a valid Terraform plan file at "head.json" with no resource changes
    When the operator runs diff with base "base.json" and head "head.json"
    Then the command exits with status 0
    And resources with missing address are indexed with empty string

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator validates output JSON structure
    Given a valid Terraform plan file at "base.json" with no resource changes
    And a valid Terraform plan file at "head.json" with a resource "aws_instance.web" having actions "create"
    When the operator runs diff with base "base.json" and head "head.json"
    Then the output JSON contains exactly the keys "verdict", "notes", "findings"
    And each finding contains exactly the keys "address", "actions_before", "actions_after"
