Feature: EHR user authentication and access

  As an EHR user with role-based access
  I want to authenticate securely
  So that my access to PHI is logged and authorized

  Background:
    Given the EHR system is running
    And an audit log destination is configured

  @hipaa:(a)(2)(i) @hipaa:(d)
  Scenario: User logs in with unique credentials
    Given I am a registered clinician with username "alice.chen"
    When I authenticate with my password and second factor
    Then I should be authenticated as "alice.chen"
    And the audit log should record my unique user identifier

  @hipaa:(a)(2)(ii)
  Scenario: Break-glass access during emergency
    Given an emergency access policy is active
    And I am an authorized clinician
    When I invoke break-glass mode for patient "P-001"
    Then I should gain temporary access to the patient record
    And the audit log should record the emergency access reason

  @hipaa:(a)(2)(iv)
  Scenario: PHI is encrypted at rest
    Given a patient record exists in the database
    When I inspect the underlying storage
    Then the patient record bytes should be encrypted
    And decryption should require an authorized session key

  @hipaa:(b)
  Scenario: All PHI access is recorded
    Given a clinician views patient record "P-001"
    When the access completes
    Then the audit log should contain a record with user, patient, action, and timestamp

  @hipaa:(c)(2)
  Scenario: Tampering with patient record is detected
    Given a patient record was last modified at a known checksum
    When the record bytes are altered outside the application
    Then the next read should detect the integrity violation
    And the audit log should record the integrity alarm
