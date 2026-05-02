Feature: Password reset via email

  As a registered user I want to reset my password via email so that I
  can regain access if I forget my credentials.

  Background:
    Given the password reset service is available

  Scenario: Registered user requests a reset and receives a link
    Given a registered user with email "alice@example.com"
    When the user requests a password reset for "alice@example.com"
    Then a reset link is sent to "alice@example.com"
    And the link expires 30 minutes after issuance

  Scenario Outline: Reset endpoint responds identically regardless of email existence
    Given the email "<email>" status is "<status>"
    When a password reset is requested for "<email>"
    Then the system returns a generic success response
    And no information about account existence is leaked

    Examples:
      | email                | status       |
      | alice@example.com    | registered   |
      | ghost@example.com    | unregistered |

  Scenario: Successful reset invalidates existing sessions
    Given user "alice@example.com" has 2 active sessions
    When the user completes a password reset
    Then all existing sessions for "alice@example.com" are invalidated
