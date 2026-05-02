# User Story: Password Reset

**As a** registered user
**I want to** reset my password via email
**So that** I can regain access to my account if I forget my credentials

## Acceptance Criteria

1. User can request a password reset by entering their registered email.
2. If the email exists, a reset link is sent; the link expires after
   30 minutes.
3. If the email does not exist, the system returns the same response as
   the success case to avoid leaking account existence.
4. The reset link can be used at most once.
5. After successful reset, all existing sessions for the user are
   invalidated.
