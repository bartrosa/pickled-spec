@gdpr-web-crud:right-to-erasure
@gdpr-web-crud:storage-limitation
@gdpr-web-crud:audit-logging
@gdpr-web-crud:data-subject-identification
@schema:endpoint:DELETE-/users/{id}
@schema:endpoint:POST-/users/{id}/erase
Feature: User-initiated account deletion

  Scenario: Authenticated user requests deletion; 30-day soft-delete
    Given an authenticated user with id "u-123"
    When they POST /users/u-123/erase with their session token
    Then their record is soft-deleted (deleted_at is set to now)
    And hard_delete_after is set to now + 30 days
    And the action is recorded in the audit log
    And subsequent GET /users/u-123 returns 410 Gone

  Scenario: Background worker hard-deletes after retention window
    Given a user record with hard_delete_after < now
    When the daily retention worker runs
    Then the record is removed from the users table
    And the deletion is recorded in the audit log
