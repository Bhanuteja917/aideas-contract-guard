# Bugfix Requirements Document

## Introduction

The ContractsList component currently uses custom Tailwind styling instead of shadcn native components, which breaks consistency with the design system. This affects three areas: table structure, action buttons, and icons. The fix will replace custom implementations with shadcn's Table component, Button component, and lucide-react icons while preserving all existing functionality and behavior.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN rendering the contracts table THEN the system uses custom HTML table elements with manual Tailwind classes (`<table className="min-w-full divide-y">`, `<thead className="bg-muted/50">`, etc.) instead of shadcn Table components

1.2 WHEN rendering the "View Analysis" action link THEN the system uses a custom `<button>` element with manual styling (`className="text-primary hover:underline"`) instead of shadcn Button component

1.3 WHEN rendering icons (refresh, upload, document, etc.) THEN the system uses inline SVG elements with manual path definitions instead of lucide-react icon components

### Expected Behavior (Correct)

2.1 WHEN rendering the contracts table THEN the system SHALL use shadcn Table components (Table, TableHeader, TableBody, TableRow, TableHead, TableCell) with native shadcn styling

2.2 WHEN rendering the "View Analysis" action link THEN the system SHALL use shadcn Button component with appropriate variant (e.g., `variant="link"`) to maintain the link appearance

2.3 WHEN rendering icons THEN the system SHALL use lucide-react icon components (RefreshCw, Plus, FileText, etc.) instead of inline SVG elements

### Unchanged Behavior (Regression Prevention)

3.1 WHEN contracts are loaded and displayed THEN the system SHALL CONTINUE TO show all contract information (fileName, fileSize, uploadedAt, status) in the same table structure

3.2 WHEN clicking "View Analysis" on a completed contract THEN the system SHALL CONTINUE TO navigate to the dashboard page for that contract

3.3 WHEN clicking the "Refresh" button THEN the system SHALL CONTINUE TO reload the contracts list from the API

3.4 WHEN clicking the "Upload Contract" button THEN the system SHALL CONTINUE TO navigate to the upload page

3.5 WHEN hovering over table rows THEN the system SHALL CONTINUE TO show hover effects indicating interactivity

3.6 WHEN the contracts list is empty THEN the system SHALL CONTINUE TO display the empty state message with upload prompt

3.7 WHEN contracts are loading THEN the system SHALL CONTINUE TO display the loading skeleton

3.8 WHEN there is an error loading contracts THEN the system SHALL CONTINUE TO display the error alert with retry option

3.9 WHEN displaying contract status THEN the system SHALL CONTINUE TO show the appropriate Badge component with correct variants

3.10 WHEN formatting dates and file sizes THEN the system SHALL CONTINUE TO use the same formatting functions
