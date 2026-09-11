severity: blocker

A1. 資安席「涵蓋判定輪」只比對檔名、不比對內容——同一支檔換掉內容也算「已審過」
判定輪 `snapshot_path` 抽出的檔名集合(`jfiles`)只跟資安席歷史上審過的檔名集合(`sfiles`)做**檔名**差集,`_patch_files_from_text` 回的是檔名字串集合,完全不含內容雜湊。實測:r1 由 `資安-sonnet` 審過 `app/login.py`(內容 A,clean);r2(判定輪,無資安席)把 `app/login.py` 改成完全不同的新內容(模擬新注入的漏洞)後單獨送審——`loop status --disposal` 直接 rc0 PASS,還印「資安席: ✓ — r1 資安-sonnet(看過的檔涵蓋最後一版 1 個)」,但 r1 資安席從未看過 r2 那版內容。
最小重現(已實跑):在 `/tmp/secrepro/run_repro.py` 建 r1(`app/login.py`="SAFE-V1",`資安-sonnet`+`正確性-sonnet` 都審過)、r2(`app/login.py`="VULN-V2-NEW-SQLI",只有 `邊界-sonnet` 審,無資安席),`lumos loop status code-secstale-demo --disposal --spec r2.patch --repo <root>` 輸出:
```
[disposal] 資安席: ✓ — r1 資安-sonnet(看過的檔涵蓋最後一版 1 個)
✅ DISPOSAL GATE PASS (code-secstale-demo 輪 r2: ...)
```
severity: blocker
blocking: 是
引句:「它看過的檔(凍結 patch 檔案清單聯集)涵蓋判定輪全部檔,否則問閘不過。」
file: `scripts/lumos:15023-15026` `sfiles`/`missing` 只用 `_patch_files_from_text` 回傳的檔名集合做差集運算,無任何內容雜湊比對。

A2. loop id 沒帶連字號(如 `codestage9`)時,`_gated_seats_for` 直接整步 skip——資安席規則可被命名方式完全繞過,而姊妹步驟(條款綁定)早就為同一漏洞修過
`_gated_seats_for` 第一行就判 `_roster_kind(loop_id or "") != "code"` → 回 `skip`;但 `_roster_kind` 對「`code` 開頭卻沒有連字號」的 id(docstring 自己舉例 `codestage`,還註明「歷史帳實有」)回 `None`,不等於 `"code"`,於是資安席整步被跳過。同一支 diff 緊鄰的 `_disposal_clause_step` 明確寫著「code 開頭但不是 code- 的一律當設計審,fail-closed」,原因就是之前有人用這招繞過——但這個修法沒有被套用到新加的資安席步驟上。
最小重現(已實跑):loop id 取 `codestage9-mdbypass-demo`(無連字號)、`--tier high`、只派 `正確性-sonnet`(無資安席)、`--spec` 給一份完全沒有 `[SN]` 標記的普通 `.md`(讓條款綁定也判 skip)。`lumos loop status codestage9-mdbypass-demo --disposal --spec r1.md --repo <root>` 輸出:
```
[disposal] 條款綁定: —(計劃無 [SN] 條款,opt-in 未啟用)
[disposal] 資安席: —(設計審不要求資安席——設計審編制不加)
✅ DISPOSAL GATE PASS (codestage9-mdbypass-demo 輪 r1: ...)
```
rc=0,tier=high 的「code」審查全程沒有一席資安、也沒有真正的凍結 diff 當 `--spec`,問閘仍然全綠放行。
severity: blocker
blocking: 是
引句:「code 開頭但不是 code- 的一律當設計審,fail-closed;不看副檔名——外家席:.patch 跳過只看尾碼會被設計審拿 patch 當審材繞過」
file: `scripts/lumos:14944-14945` `_gated_seats_for` 對非精確 `"code"` 的 `_roster_kind` 結果一律 skip,未比照 `_disposal_clause_step` 的 fail-closed 處理。

LUMOS-IMPACT 固定席逐條判(b4926d9c..HEAD):
- `Systems/design-loop.md`(★INVARIANT★ 處置閘第五步/條款綁定):這份 diff 沒改條款綁定本體邏輯,153 個 disposal 相關測試全綠,不影響其宣稱行為;但 A2 指出新加的第六步(資安席)沒有沿用條款綁定當初為了同一種繞過方式(indeterminate id)而定的 fail-closed 準則,兩步對「非 code- 前綴 id」的處置從此不一致。
- `Systems/bound-tests-gate.md`(★INVARIANT★ code-loop check 對固定席測試的紅/懸空/unfilterable 判 blocked,沒 run_cmd 則不擋只記帳):不影響——懸空/偽證據/壞名的判斷仍在檢查 `run_cmd` 是否存在**之前**執行(`scripts/lumos:22297-22301` status!=real 先攔),多平台缺指令只是把「沒 run_cmd」的粒度從整批改成逐平台,沒 run_cmd 仍是不擋只記帳,跟原 INVARIANT 一致。
- `Systems/canary-audit.md`(★INVARIANT★ record/second 落盤可讀回、second 不影響 rc):本次 diff 未觸碰 `cmd_canary`/`cmd_canary_second` 的寫入或落盤驗證邏輯,不影響。
- `Systems/guard-kill.md`(★INVARIANT★ rc 優先序、--json 純度):`cmd_guard_kill` 唯一改動是把內聯 JSON 讀取抽成 `_config_has_top_run_cmd`,列印的字串與 `file=` 目的地完全沒變(逐字比對過),不影響 rc 邏輯與 JSON 純度。
- `Systems/slim-install-安裝器.md` / `Systems/slim-uninstall-一行卸載.md` / `Systems/slim-get-一行安裝.md`:此 diff 不觸及任何安裝器/卸載器/`.ps1` 相關程式碼路徑,不影響。
- `Systems/canary record 未落盤事件.md`:本次未改動落盤驗證函式,不影響。

總結:最嚴重 severity 為 blocker,blocking 共 2 條(A1、A2)。
