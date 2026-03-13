# Implementation Plan

- [ ] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Shadcn Native Components Usage
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate custom HTML/styling is used instead of shadcn components
  - **Scoped PBT Approach**: Scope the property to the concrete failing cases - custom table elements, custom button styling, and inline SVG icons
  - Test that ContractsList component uses custom HTML table elements (`<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`) with manual Tailwind classes instead of shadcn Table components
  - Test that "View Analysis" action uses custom `<button>` element with `className="text-primary hover:underline"` instead of shadcn Button component
  - Test that icons (refresh, upload, document) are rendered as inline `<svg>` elements with `<path>` children instead of lucide-react icon components
  - Test that component imports do NOT include Table components or lucide-react icons
  - The test assertions should verify that shadcn Table components, Button with variant="link", and lucide-react icons ARE used (this is the expected behavior)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found: specific DOM elements showing custom implementations
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Functional Behavior Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for all functional operations (navigation, data loading, formatting, status display, error handling, empty states)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Test navigation: clicking "View Analysis" navigates to `/dashboard/{contractId}` for completed contracts
  - Test data loading: clicking "Refresh" calls `loadContracts()` and updates contracts state
  - Test upload navigation: clicking "Upload Contract" navigates to `/upload` page
  - Test formatting: `formatDate()` and `formatFileSize()` produce consistent output for various inputs
  - Test status badges: correct Badge variants display for each status (completed, processing, failed, pending)
  - Test empty state: "No contracts" message displays when contracts array is empty
  - Test loading state: loading skeleton displays while `loading` is true
  - Test error state: error alert displays when `error` is set
  - Test hover effects: table rows show visual feedback on hover
  - Test conditional actions: action column shows correct text based on contract status
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_

- [ ] 3. Fix for ContractsList shadcn styling

  - [ ] 3.1 Install shadcn Table component
    - Run: `npx shadcn@latest add table` to install the Table component
    - Verify installation creates `frontend/src/components/ui/table.tsx`
    - _Requirements: 2.1_

  - [ ] 3.2 Add icon imports
    - Import lucide-react icons at the top of `frontend/src/components/ContractsList.tsx`
    - Add: `import { RefreshCw, Plus, FileText } from 'lucide-react';`
    - _Requirements: 2.3_

  - [ ] 3.3 Add Table component imports
    - Import shadcn Table components in `frontend/src/components/ContractsList.tsx`
    - Add: `import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from './ui/table';`
    - _Requirements: 2.1_

  - [ ] 3.4 Replace table structure with shadcn Table components
    - Replace `<table className="min-w-full divide-y">` with `<Table>`
    - Replace `<thead className="bg-muted/50">` with `<TableHeader>`
    - Replace `<tbody className="divide-y">` with `<TableBody>`
    - Replace all `<tr>` elements with `<TableRow>`
    - Replace all `<th>` elements with `<TableHead>`
    - Replace all `<td>` elements with `<TableCell>`
    - Remove custom Tailwind classes that are now handled by shadcn components
    - Keep the `overflow-x-auto` wrapper div for responsive scrolling
    - Preserve text alignment (left for most columns, right for Actions)
    - _Bug_Condition: isBugCondition(element) where element.type == 'table' AND hasCustomTailwindClasses(element)_
    - _Expected_Behavior: usesShadcnComponents(result) where element.type IN ['Table', 'TableHeader', 'TableBody', 'TableRow', 'TableHead', 'TableCell']_
    - _Preservation: All contract data display, table structure, and hover effects must remain unchanged_
    - _Requirements: 2.1, 3.1, 3.5_

  - [ ] 3.5 Replace "View Analysis" button with shadcn Button component
    - Replace `<button onClick={() => handleViewContract(...)} className="text-primary hover:underline">View Analysis →</button>`
    - With: `<Button variant="link" onClick={() => handleViewContract(...)}>View Analysis →</Button>`
    - _Bug_Condition: isBugCondition(element) where element.type == 'button' AND element.className == 'text-primary hover:underline'_
    - _Expected_Behavior: usesShadcnComponents(result) where element.type == 'Button' AND element.variant == 'link'_
    - _Preservation: Navigation to dashboard page must remain unchanged_
    - _Requirements: 2.2, 3.2_

  - [ ] 3.6 Replace refresh icon with lucide-react RefreshCw
    - Replace the inline SVG element in the Refresh button
    - With: `<RefreshCw className="h-4 w-4 mr-2" />`
    - _Bug_Condition: isBugCondition(element) where element.type == 'svg' AND isInlineSVG(element)_
    - _Expected_Behavior: usesShadcnComponents(result) where element.type == 'RefreshCw'_
    - _Preservation: Refresh button functionality must remain unchanged_
    - _Requirements: 2.3, 3.3_

  - [ ] 3.7 Replace upload icon with lucide-react Plus
    - Replace the inline SVG element in the Upload Contract button
    - With: `<Plus className="h-4 w-4 mr-2" />`
    - _Bug_Condition: isBugCondition(element) where element.type == 'svg' AND isInlineSVG(element)_
    - _Expected_Behavior: usesShadcnComponents(result) where element.type == 'Plus'_
    - _Preservation: Upload navigation must remain unchanged_
    - _Requirements: 2.3, 3.4_

  - [ ] 3.8 Replace document icons with lucide-react FileText
    - Replace the inline SVG in table rows (next to file names)
    - With: `<FileText className="h-5 w-5 mr-2 text-destructive" />`
    - Replace the inline SVG in the empty state
    - With: `<FileText className="mx-auto h-12 w-12 text-muted-foreground" />`
    - _Bug_Condition: isBugCondition(element) where element.type == 'svg' AND isInlineSVG(element)_
    - _Expected_Behavior: usesShadcnComponents(result) where element.type == 'FileText'_
    - _Preservation: File display and empty state must remain unchanged_
    - _Requirements: 2.3, 3.1, 3.6_

  - [ ] 3.9 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Shadcn Native Components Usage
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - Verify DOM contains shadcn Table components (Table, TableHeader, TableBody, TableRow, TableHead, TableCell)
    - Verify "View Analysis" action uses shadcn Button component with variant="link"
    - Verify all icons are lucide-react components (RefreshCw, Plus, FileText)
    - Verify component imports include Table components and lucide-react icons
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 3.10 Verify preservation tests still pass
    - **Property 2: Preservation** - Functional Behavior Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - Verify navigation to dashboard works for completed contracts
    - Verify refresh button reloads contracts from API
    - Verify upload button navigates to upload page
    - Verify date and file size formatting produces same output
    - Verify status badges display with correct variants
    - Verify empty state displays correctly
    - Verify loading skeleton displays correctly
    - Verify error alert displays correctly
    - Verify hover effects work on table rows
    - Verify conditional actions display correctly based on status
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
