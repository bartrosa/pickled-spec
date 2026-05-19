@gdpr-web-crud:lawfulness-of-processing
@gdpr-web-crud:consent-management
@gdpr-web-crud:data-minimization
@gdpr-web-crud:privacy-by-design
@gdpr-web-crud:cookie-consent
@gdpr-web-crud:childrens-data
@schema:endpoint:POST-/users
Feature: User registration with explicit consent

  Scenario: New user registers with marketing consent declined by default
    Given no account exists for email "new@example.com"
    When they POST /users with email, name, and consent_marketing false
    Then the response status is 201 Created
    And consent_at is stored with the registration timestamp
    And only required profile fields are persisted

  Scenario: Under-age applicant is rejected
    Given the applicant declares age 15
    When they POST /users
    Then the response status is 403 Forbidden
    And no users row is created
