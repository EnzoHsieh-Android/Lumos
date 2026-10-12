severity: major

severity: major
blocking: 是
F1：`collect_only: true` 但省略 `expect` 時會通過前置驗證，模型執行完才在 `grade()` 取 `sc["expect"]` 時崩潰，浪費額度並中止批次；file: `scripts/scenario_probe.py:321`、file: `scripts/scenario_probe.py:817`。
引句:「if not sc.get("expect") and sc.get("collect_only") is not True:」
重現: `python3.14 -c 'import runpy; m=runpy.run_path("scripts/scenario_probe.py",run_name="sp"); s={"id":"q","prompt":"p","collect_only":True}; print(m["_validate_scenario"](s)); m["grade"](s,[],"answer")'` → `None`，接著 `KeyError: 'expect'`。

severity: major
blocking: 是
F2：續跑用的版本紀錄未納入題庫內容與甲乙 repo 版本，因此更換 `--scenarios` 或兩組受測 repo 後，舊的有效結果仍會被當成相符而跳過，污染對照實驗；file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:190`。
引句:「meta = {"runner": a.runner, "model": a.model, "cli": _cli_version(a.runner), "answer_max": ANSWER_MAX}」
重現: `python3.14 -c 'import runpy,inspect; f=runpy.run_path("governance/eval/qo-ablation-2026-10/qo_ablation.py",run_name="qo")["cmd_run"]; s=inspect.getsource(f); m=s[s.index("meta ="):s.index("jobs =")]; print(m.strip()); assert "a.scenarios" in m and "a.arm_a" in m and "a.arm_b" in m'` → 印出的 meta 只有 runner/model/CLI/answer_max，隨即 `AssertionError`。

severity: major
blocking: 是
F3：`final` 雖重讀目前的 mapping 與兩份標註，卻直接採信任意 `--agree` 檔內的 kappa，沒有核對它是否由同一批 mapping／標註產生；舊 agree 檔可讓實際一致率低於 0.6 的結果從 INCONCLUSIVE 變成 PASS，file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:469`。
引句:「agree = json.loads(Path(a.agree).read_text(encoding="utf-8"))」
重現: `python3.14 -c 'import runpy; q=runpy.run_path("governance/eval/qo-ablation-2026-10/qo_ablation.py",run_name="qo"); s={"truncated_any":False,"kappa":1.0,"complete":6,"all_zero":False,"mean_diff":1.0,"p":1/64,"noise_a":0,"noise_b":0,"code_a":0,"code_b":0}; print(q["verdict"](s)[0],q["verdict"]({**s,"kappa":1/3})[0])'` → `PASS INCONCLUSIVE`。

總結:最嚴重 major;blocking 共 3 條
