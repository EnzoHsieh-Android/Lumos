# README diagram source

Seven bilingual scenes share one visual system without sharing one layout.
The generator uses only the Python standard library and writes the existing
SVG filenames used by the READMEs. Logos, the recorded GIF, and the detailed
diagrams in docs are outside its scope.

```bash
python3 assets/readme-diagrams/generate.py
python3 assets/readme-diagrams/generate.py --check
```

The check validates XML, reproduces all 14 assets exactly, and ensures that
animation is confined to decorative paths or borders, except for the knowledge
scene's explicit node-reveal timeline.
The knowledge scene also checks its plan-to-feature-to-verification relations,
incident feedback links, and two contract rings. Decorative pictogram icons
are intentionally omitted; nodes, rings, contract stars, arrows, and step numbers carry meaning.
Its 24-second cycle reveals plans, features, verification, contract rings, an
incident, a points-return repair plan, and regression verification. It holds
the complete graph for 12.2 seconds. The repair targets the existing checkout
feature; this illustration assumes checkout owns the points-return behaviour.
Checks enforce reveal order, rings after evidence, and a complete static fallback.
Run it after changing the source. Do not hand-edit generated SVGs.

Visual checks are still required: render both languages, inspect long English
labels and connector routing, and check a narrow preview. The 13–14 px labels
are secondary identifiers; the main labels are larger and explained in the
surrounding README. Each README image links to its full-size SVG.

Scene roles:

- Map: development loop with an outer evaluation feedback path.
- First change: conversation beside the AI execution timeline.
- Knowledge: four rows separating plans, features, verification, and incidents,
  with contract rings on features and an incident → repair plan → existing
  feature → regression verification feedback path.
- Dispatch: shared materials fan out to independent review perspectives.
- Review: architecture context above complementary evidence sources.
- Write-back: work records become retrievable notes.
- Evals: review replay and retrieval evaluation inform calibration.

These are conceptual illustrations, not screenshots, benchmark reports, or
claims of guaranteed correctness. The map retains a moving loop; every scene
is complete and readable when animation is unavailable.
