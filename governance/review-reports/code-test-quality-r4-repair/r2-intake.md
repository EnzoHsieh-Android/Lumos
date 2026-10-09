# r2 intake

preflight-4: ran

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| R4-R2-REG-1 | regression | minor | HIT | folded | global vault subprocess now runs in `self.root` where its relative source exists |
| MT-1 | mutation | major | HIT | folded | deleting the source fixture previously stayed green; corrected cwd makes the fixture part of the exercised path |
| B1 | boundary | major | HIT | folded | fake backend worker survived before shared process-group runner and stops after it |
| A1 | architecture | minor | HIT | folded | out-of-range finding now enters through fake Semgrep and asserts structured unavailable output |

R4-R2-REG-1, MT-1 and A1 are attributable to the r1 evidence repair. B1 is a pre-existing sibling runner gap found while checking the unified cleanup policy. During the fold, targeted controls also caught and fixed a double-cleanup PermissionError and the frozen corpus missing the new transitive core sidecar.
