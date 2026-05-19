@gdpr-web-crud:purpose-limitation
@gdpr-web-crud:breach-notification
@gdpr-web-crud:international-transfers
@gdpr-web-crud:processors
@gdpr-web-crud:encryption-in-transit
@gdpr-web-crud:encryption-at-rest
@gdpr-web-crud:automated-decision-making
@schema:endpoint:POST-/privacy/consents
@schema:endpoint:GET-/privacy/policy
@schema:endpoint:POST-/breaches/notify
Feature: Privacy transparency, breach routing, and platform safeguards

  @gdpr-web-crud:consent-management
  Scenario: Subject records marketing consent withdrawal
    Given an authenticated user with id "u-100"
    When they POST /privacy/consents with purpose "marketing" and granted false
    Then the response status is 201 Created
    And the consent row reflects withdrawal timestamp

  @gdpr-web-crud:dpo-contact
  Scenario: Public policy page lists privacy contact
    When a client GET /privacy/policy
    Then the response status is 200 OK
    And the body includes a privacy contact email

  Scenario: Operator files an internal breach notice
    Given a security operator with an internal service token
    When they POST /breaches/notify with severity and affected scope
    Then the response status is 202 Accepted
    And no personal data is echoed in the response body

  Scenario: Risk score defers to human review
    Given a fraud score flags user "u-200"
    When the automated decision service recommends account lock
    Then a human analyst must approve before the account status changes
    And the logic summary is available to the subject on request

  @gdpr-web-crud:records-of-processing
  @gdpr-web-crud:dpia
  @gdpr-web-crud:joint-controllers
  @gdpr-web-crud:pseudonymization
  Scenario: Processing inventory references the user table
    Given an internal processing register lists the users table purpose
    When operators review the register quarterly
    Then each API flow maps to a documented purpose and retention period
    And audit payloads use pseudonymous actor tokens where possible
