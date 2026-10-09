# r1 intake

preflight-4: ran

| id | source | severity | reproduce | disposition | evidence |
|---|---|---|---|---|---|
| R4-COR-1 | correctness | minor | HIT | folded | `test_semgrep_findings_decode_once_and_reject_out_of_range_line` distinguishes one decode plus valid and invalid locations |
| R4-COR-2 | correctness | minor | HIT | folded | global vault control now runs with `cwd=self.root` where its valid source exists |
| A1 | architecture | major | HIT | folded | `test_failed_capture_stops_stream_detached_worker` red before unconditional group cleanup and green after |
| SEC-R4-1 | security | major | MISS | refuted | portable contract covers the process group created by Lumos; deliberate setsid escape needs platform isolation and is outside the trusted-command contract |

The defender independently reproduced A1 and rejected SEC-R4-1 as a contract expansion rather than a defect. Windows remains outside this verification.
