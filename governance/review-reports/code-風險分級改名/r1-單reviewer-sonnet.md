severity: major

## F1 pitfalls 在 pre-push 熱路徑上會把「留痕裡的測試」重跑第二次,跟 spec-gate --push-check 重複
severity: major
blocking: yes

引句:「先用便宜的前置(審查帳裡有沒有全靠人驗的風險低留痕)決定要不要載入圖譜——pitfalls 在 pre-push 熱路徑上,圖譜載入要幾秒。」
引句:「if not ledger.exists() or '"manual_only": true' not in ledger.read_text(encoding="utf-8", errors="replace"):」
引句:「bad, oks = _spec_gate_push_report(env, Path(repo_root).resolve(), diff_range)」

觀察:
`_pitfall_plan_light`(scripts/lumos:22249)的「便宜前置」只檢查 `.canary-log.jsonl` 這個檔**裡有沒有任何一筆** `"manual_only": true`,不管那筆記錄是不是這次 diff 範圍碰到的計劃。這個 repo 本身已經有多份全靠人驗的風險低計劃留過痕(見 CLAUDE.md/memory 提到的「風險低 doing」「manual_only」若干筆),所以這個前置幾乎永遠成立、幾乎每次 push 都會往下走。

往下走之後呼叫 `_spec_gate_push_report`(scripts/lumos:5825 一帶)→ `_spec_gate_push_scan(..., quiet=True)` → `_spec_gate_push_one`(scripts/lumos:5775)。對「有綁測試(非全靠人驗)」的風險低候選計劃,`_spec_gate_push_one` 會走：

```
results, rerr = _run_bound_tests(rr, items, tails=tails)
```

也就是**真的把留痕裡綁的測試跑一次**,不是只讀留痕。

而 `pre-push` 這支 hook 對**每一個要推的 ref 都無條件**呼叫一次 `pitfalls --diff ... --json`(scripts/hooks/pre-push:209-210):

```
pf_json="$("$PY" "$GRAPHCTL" pitfalls --diff "$_range" --no-lint --json --repo "$REPO_ROOT" 2>/dev/null || true)"
```

這條路徑不看 tier 是不是 high,是每次都跑,為的就是先算出 `tier` 給後面用。跑完之後,同一支 hook 接著在（r1-snapshot.patch 行 18-19）又呼叫一次：

```
"$PY" "$GRAPHCTL" spec-gate --push-check "$_range" --repo "$REPO_ROOT" >&2 || sg_rc=$?
```

`spec-gate --push-check` 走的是 `_spec_gate_push_check` → `_spec_gate_push_scan(..., quiet=False)` → 同一支 `_spec_gate_push_one`,對**同一個 `$_range`**、同一批風險低候選計劃再跑一次同一批綁定測試。

重現:一份 repo 裡只要曾經留過至少一筆 `manual_only: true` 的 spec-gate 記錄(這個 repo 已經有),且這次要推的分支剛好也碰到另一份「風險低、但有綁測試(非全靠人驗)」的 doing 計劃,那麼 `git push` 這一輪會把該計劃留痕裡的每一支綁定測試**各跑兩次**——一次在算 `tier` 的 `pitfalls --json`裡(靜默跑,結果只拿來決定要不要印 tier_reason,若這次沒過就直接丟棄,連原因都不會浮現),一次在真正的 `spec-gate --push-check` 擋関裡。

為什麼是 bug:docstring 自己講的設計目的是「便宜的前置」+「pitfalls 在熱路徑上要控制成本」,但實作出來的效果是:條件一旦成立(而且很容易成立,因為前置檢查沒有 scope 到當次候選計劃),反而在熱路徑裡多跑一輪原本只在 `--push-check` 才會跑的真實測試套件,讓每次 push 多花一份「跑綁定測試」的時間、且是白跑(結果只用來判斷要不要把 tier 標成 light,真正擋不擋還是看後面 `--push-check` 那次)。這正是這次派工單特別點名要查的「`_pitfall_plan_light` 在 pre-push 熱路徑的成本」踩到的洞。

## F2 `_sc_diffusion`/`_pitfall_tier` 的「需要有家的程式檔」判斷沒有真的和「每支檔有家」同一套定義,extensionless 非 shebang 檔(如 .gitignore)會被誤算成程式檔
severity: major
blocking: yes

引句:「code = [f for f in files if _nodehome_code_kind(f[0]) is not None]   # 擴散與落點只算需要有家的程式檔;文件/圖/資料只在相對量那一維度算(2026-09-18:README+圖把目錄數撐破)」
引句:「code = [f for f in files if not (f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIRS)) and _nodehome_code_kind(f) is not None]」
引句:「回 'ext'(副檔名在清單裡)/'shebang?'(沒副檔名,要看首行)/None(不是程式檔)。」

觀察:
兩處新增的「code」過濾(scripts/lumos:5660 的 `_sc_diffusion`,scripts/lumos:22240 的 `_pitfall_tier`)都只用 `_nodehome_code_kind(f) is not None` 判斷「是不是需要有家的程式檔」,並在註解裡宣稱這是跟「每支檔有家」同一套定義(「每支檔有家同一套定義 _nodehome_code_kind」)。

但 `_nodehome_code_kind`(scripts/lumos:20650)本身對沒有副檔名的檔案只回 `"shebang?"`,意思是「要看首行才能判定」,不是「確定是程式檔」。真正的「每支檔有家」機制 `_nodehome_required`(scripts/lumos:20811 一帶)對 `kind == "shebang?"` 還會**再讀檔案首行**確認真的是 `#!` 開頭才算數（不是就 `continue` 跳過,不算需要有家）：

```
if kind == "shebang?":
    ...
    ok = side.shebang[p] = bool(head) and head[:200].split(b"\n", 1)[0].startswith(b"#!")
    if not ok:
        continue
```

而這次改動裡的兩處新 `code` 過濾**都沒有做這第二步**,只看 `is not None`。結果是:任何沒有副檔名、也不是 shebang 腳本的檔案(例如 `.gitignore`、`.env`、`LICENSE`、`Makefile` 這類常見 extensionless 檔;`_nodehome_code_kind` 對它們一律回 `"shebang?"` ≠ None)都會被誤判成「需要有家的程式檔」。

為什麼是 bug:
- 在 `_sc_diffusion`(全靠人驗風險低計劃的小改動閘,scripts/lumos:5657):這種檔案會被算進 `擴散` 的檔數/目錄數,還會被拿去跟 `allowed`(計劃 lands_in 節點的 about_code)比對「落點外」——一份真正很小的改動,只因為順手改了 `.gitignore`,就可能被判「落點外」或「擴散超標」而擋下,逼你補測試或升成風險高走設計審,跟改動實際風險不成比例。
- 在 `_pitfall_tier`(scripts/lumos:22234):`if not code: return "light", ...` 這個「改動裡沒有程式檔」的判斷會因為誤把 `.gitignore` 這類檔算進 `code` 而失效,原本應該判 light 的純文件/設定改動被迫繼續往下走(進 `_pitfall_plan_light` 或落到 `standard`),跟 docstring 宣稱的「同一套定義」矛盾——兩處新邏輯事實上比「每支檔有家」的真實判準更寬,會誤傷合法的小改動。

這正是派工單邊界清單裡點名的「`_pitfall_tier` … 對 shebang 無副檔名檔」那條,兩處都踩到同一個洞(擴散閘與分級各一處,是同一個形狀重複兩次,建議一次改共用邏輯或直接呼叫 `_nodehome_required` 同一套判定,而不是各自淺用 `_nodehome_code_kind`)。

共 2 條,severity 最高 major。
