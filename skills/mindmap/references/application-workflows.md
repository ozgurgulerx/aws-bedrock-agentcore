# Application workflows

These are observed behaviors from MindNode and XMind in November 2026, not permanent API contracts. Inspect the current UI before acting.

## MindNode

- View Options → Outline exposes topic text and hierarchy clearly. Select the row rather than entering text-edit mode when adding notes or links.
- Toolbar Notes opens a node note. Use it for examples and secondary reference links; verify persistence after closing and reopening.
- Node → Add Link opens a URL popover. Set the URL field, read the updated state, then activate Add Link. Node → Edit Link can inspect the destination; Open Link follows it.
- A link can underline the entire node text. A click may open a link preview rather than immediately navigate. Explain the actual interaction observed; do not promise one-click navigation if the app presents Open Link.
- AX link values may omit the https scheme even when the editor contains a complete https URL. Inspect the editor or navigation before diagnosing a broken link.
- Multiline typing into a node can create sibling nodes. For multiline node content, use the supported text-entry set-value operation and verify the resulting hierarchy. Multiline text in Notes behaved as note content.
- Node → Size to Fit Content can restore widths in map view. It may be disabled in outline view or while editing text. Exit text editing, select only the intended nodes, and inspect the result.
- After actions, refresh accessibility state before deriving the next indices. If the app reports that the user changed it, re-query and respect the current state. Do not continue with stale menu indices.
- Menu/popover dismissal can be delayed or incompletely reflected in accessibility output. Use a screenshot when the tree and expected result disagree; avoid repeating writes blindly.

## XMind import

- A MindNode FreeMind (.mm) export was accepted by XMind's other-mindmap-formats import flow.
- Import preserved the hierarchy and examples in notes in this session, but altered whitespace, wrapping, and some colors. Verify these features for each import, including hyperlinks added after an earlier export.
- White text imported onto a white canvas made the map look empty. Inspect actual node content and canvas contrast before concluding import failed. A dark background restored readability in that case; preserve the user's design preference.
- Fit Map helps find imported content. Ensure the document is actually visible in the intended browser window.
- A previously working XMind document later opened as a blank Safari page. A URL alone is not evidence of a successful import or saved edit. Do not create duplicate maps as a workaround without making the consequence clear.

## Completion checks

- Correct original/copy and document title.
- Expected nodes and hierarchy, no accidental siblings or replacements.
- Notes retain examples and existing content.
- Native hyperlinks point to the intended official sources.
- Legible contrast and wrapping; no hidden off-canvas result mistaken for success.
- Report unverified browser navigation separately from successfully saved links.
