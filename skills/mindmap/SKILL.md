---
name: mindmap
description: Create, extend, or refine learning mindmaps in MindNode or XMind, with concise topic nodes, examples in notes, and clickable source links. Use for mindmap editing and migration requests.
---

# Mindmap

Build an editable learning map in the user's chosen application. Default to the existing original map when that choice is established; do not migrate products merely because automation is easier elsewhere.

## Content and hierarchy

- Inspect the existing map and preserve its vocabulary, hierarchy, notes, and styling before editing.
- Organize concepts by meaningful relationships. Distinguish a service, its resources, implementation choices, hosting, and architectural patterns instead of treating them as interchangeable siblings.
- Keep node titles short. Use brief bullets for parallel facts. Put extended explanations, code, caveats, and concrete examples in native node notes/comments.
- Prefer private node notes for learning examples; do not post collaborative comments or notify others unless requested. If notes are unavailable, use a compact Example child node and explain that fallback.
- Use connections for real cross-topic dependencies; label them when the relationship is not obvious.
- For study maps, distinguish covered topics from demonstrated mastery. Do not infer completion or a percentage merely from the number of nodes.

## Examples and references

For each substantive topic where useful:

1. Add a brief example to its note: situation → action/flow → result. Preserve existing notes, appending only nonduplicative content.
2. Find the most specific relevant official documentation page. Verify current technical features and URLs with authoritative sources; do not invent links from naming conventions.
3. Attach the primary URL using the app's native hyperlink feature so the node opens the source. Put additional sources in its note with descriptive labels.
4. Match the source to the actual product and topic. For example, an AgentCore/Strands coordination topic should not silently link to Bedrock Agents classic multi-agent collaboration.
5. Treat examples as illustrative, not proof of product capabilities. Record meaningful support constraints in notes rather than cluttering the canvas.

Suggested note:

```text
Example — Order assistant
User asks where an order is → model requests get_order → application checks
authorization and calls the tool → tool result returns → model answers.

Important distinction: a tool request does not authorize access.
Documentation: [specific official page URL]
```

## Editing and verification

- Prefer a capable dedicated integration; otherwise use the available computer-use tool for app interaction. Follow its current documentation, refresh UI state after actions, and never hardcode observed element indices into a reusable workflow.
- Make reversible edits to the authorized map. If several copies are plausible and context cannot resolve the target, ask which copy before changing one.
- Use outline view for precise topic selection and map view for layout inspection. Verify parent/child placement after structural changes.
- Respect the user's preference for readable lines: fit node width to content where practical, retain intentional bullet breaks, and avoid excessively wide prose nodes. Verify wrapping visually at a useful zoom.
- Preserve canvas/text contrast. Do not redesign the map unless requested or needed to restore readability.
- Confirm node text, notes, and hyperlink destinations in the saved app state. Test at least one representative link when practical; distinguish a saved hyperlink from verified browser navigation.
- Always leave the application in visual mindmap view when finishing, unless the user explicitly requests another final view. Outline view is temporary for editing. Close editing popovers, bring the map forward, and use a useful zoom/position so the map is visible; verify the final visual state.
- Give a concise completion report with any concrete limitations. Do not claim success based only on attempted input.

Read [application-workflows.md](references/application-workflows.md) when editing MindNode, importing to XMind, or resolving UI problems. Read [agentcore-example.md](references/agentcore-example.md) only when extending the AWS learning map or needing an example of good topic boundaries.

## Migration

Preserve the original. Export/import only when requested and verify the imported hierarchy, notes, links, multiline text, and contrast before claiming completion. Identify which copy was edited; creating an export does not prove the target app imported it. Do not recommend switching applications solely on UI automation convenience.
