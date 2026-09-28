severity: major
seat: 外家否決2-codex

## F1 decision-amend 仍會把行內清單靜默改成純量

severity: major  
blocking: 是 — 安全寫入指令會破壞合法 YAML 結構並遺失清單內容。  
引句:「if k1 > k0 and not head_val:」  
file: `scripts/lumos:24936`  
file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:189`

目前只拒絕「值寫在後續縮排行」的清單或巢狀欄。若未推決策使用合法的 flow-style YAML，例如 `alternatives: [甲, 乙]`，則 `k1 == k0` 且 `head_val` 非空，守衛不會觸發；指令會把整個清單改成純量 `alternatives: only`，寫後自驗也會通過。

最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'from importlib.machinery import SourceFileLoader; from pathlib import Path; from types import SimpleNamespace as N; m=SourceFileLoader("lumos_review","scripts/lumos").load_module(); lines=["---","decisions:","  - id: d1","    alternatives: [甲, 乙]","    context: 背景","---",""]; m._lens_git=lambda root,*a: N(returncode=0,stdout=("/repo\n" if a[:2]==("rev-parse","--show-toplevel") else ""),stderr=""); m.load_raw_for_edit=lambda p:(lines,1,5); m.atomic_write_verify=lambda p,new,key,check: print("accepted=",check({}),"new=",new[3]); m.cmd_decision_amend(N(vault=Path("/repo/docs/kg-knowledge")),"Systems/D.md","d1","alternatives","only")'
```

輸出：

```text
accepted= True new=     alternatives: only
✓ decision-amend Systems/D.md d1.alternatives 改好了(這條決策還沒推上去)
```

應在改寫前辨識並拒絕 `[...]`、`{...}` 等 flow collection，或以能保留型別的解析結果判定欄位是否為純文字。

## F2 doctor 會被其他 job 的 fetch-depth: 0 誤導

severity: major  
blocking: 是 — CI 的內容審 job 可以持續在 shallow clone 中 fail-open，而 doctor 不發出規格要求的警告。  
引句:「if "note-audit check" in body and "fetch-depth: 0" not in body:」  
file: `scripts/lumos:24974`  
file: `scripts/lumos:24403`  
file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:130`

`body` 合併所有 workflow、所有 job 後只做全域字串判斷。若 `build` job 使用 `fetch-depth: 0`，但執行 `note-audit check` 的 `audit` job 使用預設 shallow checkout，條件仍為假。後者走到 `_note_audit_resolve` 會以 rc0 跳過，doctor 也不提醒，整道 CI 防線實際失效。

直接代入新增條件：

```sh
python3 -c 'body="jobs:\n  full:\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          fetch-depth: 0\n  audit:\n    steps:\n      - uses: actions/checkout@v4\n      - run: python3 scripts/lumos note-audit check --diff x\n"; print("doctor_warns=", "note-audit check" in body and "fetch-depth: 0" not in body)'
```

輸出：

```text
doctor_warns= False
```

檢查必須至少限定在包含 `note-audit check` 的同一個 job，不能讓其他 workflow 或 job 的設定抵銷警告。

## F3 同編號超過 150 處時仍產生無上限清單

severity: major  
blocking: 是 — 明文的每份 150 行上限可被單一重複內容編號突破，判定者輸入可無限膨脹。  
引句:「if cur and (len(cur) + len(u) > _NOTE_AUDIT_BATCH or (new_head and _note_audit_head_split(rows, cur, it))):」  
file: `scripts/lumos:24476`  
file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:118`

修正把同編號的所有出現位置合成不可拆的 `u`，但只有 `cur` 非空時才檢查上限。單一編號出現 151 次時，整個單位直接放進空批次，產生 151 行清單；出現數可以任意增加。這既違反 S5，也可能使判定請求超出上下文或成本限制。

最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'from importlib.machinery import SourceFileLoader; m=SourceFileLoader("lumos_review","scripts/lumos").load_module(); rows=[{"path":"docs/x.md","id":"same","heading":"H"} for _ in range(151)]; print([len(x) for x in m._note_audit_batches(rows)])'
```

輸出：

```text
[151]
```

同編號不可拆與每份最多 150 行在此輸入下互相衝突；合併前必須明確裁定，例如拒絕並說明不可表示，或重設清單與 record 協議以支援跨批次聚合同一編號，不能靜默突破上限。

總結: 最高 severity major；blocking 共 3 條。