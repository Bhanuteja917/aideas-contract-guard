# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Complete Bidirectional Navigation
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the navigation bugs exist
  - **Scoped PBT Approach**: Scope the property to concrete failing navigation cases across auth and authenticated pages
  - Test that navigation links are present for all page combinations where isBugCondition returns true:
    - SignUp page → ForgotPassword link exists
    - SignUp confirmation screen → SignIn link exists
    - ForgotPassword email step → SignUp link exists
    - ForgotPassword reset step → SignUp link exists
    - Dashboard page → ContractGuard heading is clickable Link to /contracts
    - Upload page → ContractGuard heading is clickable Link to /contracts
  - The test assertions should match the Expected Behavior Properties from design
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found (missing links, non-clickable heading)
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Authentication Functionality
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-navigation interactions:
    - Sign In form submission and authentication flow
    - Sign Up form submission, password validation, and confirmation flow
    - Forgot Password flow (email → code → new password)
    - Layout functionality (sign out, theme switching, user email display)
    - Form state management (error messages, loading states, input values)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Test that for all non-navigation interactions, behavior remains unchanged:
    - Form submissions process correctly
    - Authentication API calls work identically
    - Error handling and validation work identically
    - Theme styling and visual consistency maintained
    - Sign out and theme switcher continue to work
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix navigation issues across authentication and authenticated pages

  - [x] 3.1 Add Forgot Password link to SignUp page
    - Update navigation links section to use `flex justify-between` layout (matching Sign In page)
    - Add Link to `/forgot-password` with text "Forgot password?" and consistent styling
    - Position alongside existing "Already have an account? Sign in" link
    - _Bug_Condition: isBugCondition({currentPage: 'SignUp', targetPage: 'ForgotPassword'})_
    - _Expected_Behavior: navigationLinkExists(result, 'ForgotPassword') AND navigationLinkNavigatesTo(result, '/forgot-password')_
    - _Preservation: Sign Up form submission, password validation, confirmation flow unchanged_
    - _Requirements: 2.1, 3.1, 3.2_

  - [x] 3.2 Add navigation links to SignUp confirmation screen
    - Add "Back to sign in" link to `/signin` below Confirm button
    - Optionally add "Back to sign up" link that resets `needsConfirmation` to false
    - Use consistent styling with other auth pages
    - _Bug_Condition: isBugCondition({currentPage: 'SignUp-Confirmation', targetPage: 'SignIn'})_
    - _Expected_Behavior: navigationLinkExists(result, 'SignIn')_
    - _Preservation: Confirmation code submission and validation unchanged_
    - _Requirements: 2.2, 3.1, 3.2_

  - [x] 3.3 Add Sign Up link to ForgotPassword email step
    - Update navigation links section to use `flex justify-between` layout
    - Add Link to `/signup` with text "Don't have an account? Sign up"
    - Position alongside existing "Back to sign in" link
    - _Bug_Condition: isBugCondition({currentPage: 'ForgotPassword-Email', targetPage: 'SignUp'})_
    - _Expected_Behavior: navigationLinkExists(result, 'SignUp') AND navigationLinkNavigatesTo(result, '/signup')_
    - _Preservation: Password reset email submission unchanged_
    - _Requirements: 2.3, 3.1, 3.2_

  - [x] 3.4 Add Sign Up link to ForgotPassword reset step
    - Add Link to `/signup` with text "Don't have an account? Sign up"
    - Maintain vertical stacking layout for three links (Resend code, Sign up, Back to sign in)
    - Use consistent styling with other auth pages
    - _Bug_Condition: isBugCondition({currentPage: 'ForgotPassword-Reset', targetPage: 'SignUp'})_
    - _Expected_Behavior: navigationLinkExists(result, 'SignUp') AND navigationLinkNavigatesTo(result, '/signup')_
    - _Preservation: Password reset submission unchanged_
    - _Requirements: 2.4, 3.1, 3.2_

  - [x] 3.5 Make ContractGuard heading clickable in Layout component
    - Import Link from 'react-router-dom'
    - Wrap `<h1>ContractGuard</h1>` with `<Link to="/contracts">`
    - Add hover state styling to indicate clickability (e.g., `hover:opacity-80 transition-opacity cursor-pointer`)
    - Ensure subtitle "AI-powered contract analysis" remains outside the Link
    - _Bug_Condition: isBugCondition({currentPage: 'Dashboard', targetPage: 'ContractsList'}) OR isBugCondition({currentPage: 'Upload', targetPage: 'ContractsList'})_
    - _Expected_Behavior: hasClickableHomeLink() AND navigationLinkNavigatesTo(result, '/contracts')_
    - _Preservation: Sign out, theme switching, user email display unchanged_
    - _Requirements: 2.5, 3.3, 3.4, 3.5_

  - [x] 3.6 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Complete Bidirectional Navigation
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - Verify all navigation links are present and functional
    - Verify ContractGuard heading is clickable and navigates to /contracts
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.7 Verify preservation tests still pass
    - **Property 2: Preservation** - Authentication Functionality
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all authentication flows work identically
    - Confirm form state management unchanged
    - Confirm theme styling and visual consistency maintained
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise
