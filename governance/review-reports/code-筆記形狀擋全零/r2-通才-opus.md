severity: major

## F1 推主線時「頂端已在主線上」恆成立:force-push 改寫 main(或 repo 首推)在 CI 整批放過,比修正前還鬆
severity: major
blocking: 是 —— 這步是「--no-verify 後盾」,正好在最該擋的情境(繞過本機掛鉤、force-push 改寫主線)從「會擋」退成「不查」,而且不留跳過帳

引句:「return None, f"{why},而且頂端已經在主線({ml[0]})上——沒有新東西"」

執行路徑:
- 工具鏈自己的 ci.yml:這步只在 push main 時跑(`.github/workflows/ci.yml:3-5` `on.push.branches: [main]`)。CI 的 checkout 是本地 main、upstream=origin/main,push 後 origin/main 就是 `$SHA` 本身(ci.yml 這步自己的註解也寫了「推 main 時 origin/main 就是這次的頂端」)。
- `_lens_push_base` 取 `_mainline_ref(remote_only=True)` → `main@{upstream}` = tip,於是 `merge-base --is-ancestor tip main@{upstream}` 恆為真 → 只要起點是 40 個 0 或本機找不到,就一律回 None=不查。
- 推 main 會走到這條的情境只有兩種:force-push 改寫主線(舊頂端不可達,`fetch-depth: 0` 也抓不到)與 repo 首推。修正前 ci.yml 的 shell 把這兩種換成空樹、lumos 再截到上線點照查;修正後直接放行。也就是說,對工具鏈自己的 CI,這次新路徑唯一能走到的結果就是 None,只帶來放行,沒有任何好處。
- 消費專案照 doctor 新給的那步貼,push main 也一樣;若消費專案的 code-loop 步驟原樣傳 before,`_codeloop_guard_verdict` 新分支同樣回 `blocked False / tier standard`,連 2.5 合約測試、3.5 表態都跳過,也不再呼叫 `_gate_failopen` 留帳(修正前走 pitfalls rc2 → fail-open 至少有帳)。
- 回 None 時 cmd_note_shape / cmd_home_check 都只印一行 stderr,沒有 `_gate_event_or_warn(... "skipped-env" ...)` 這類治理帳,事後查不到被放過。

最小重現(已實跑):`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/HF2/r2-通才-opus-f1-repro.py`
步驟:本機 main 推兩個提交到裸遠端 → amend 第二個、塞進一篇新寫 `src/a.py:6` 的筆記、`--no-verify --force` 推 main → 另開一份 clone 模擬 CI(舊頂端不在 clone 裡、main@{upstream}=新頂端)→ 跑 `note-shape --diff <舊頂端>..<新頂端>`。
- 修正後(before 原樣交給工具):rc 0,訊息「起點在本機找不到,而且頂端已經在主線(main@{upstream})上——沒有新東西」
- 修正前(ci.yml 換空樹):rc 1,擋下 `docs/kg-knowledge/Systems/New.md:17 程式行號引用 src/a.py:6`

測試假綠:`t_push_base_zero_or_missing` ③ 的「force-push 後照分岔點查、不放行」只在功能分支(release-1)上驗;⑦第二條還把「頂端在主線上 → 沒有新東西」當正確行為鎖住,沒有一條驗「推的就是主線本身」。
修法方向:推的 ref 就是主線(tip == 主線頂端,或 CI 的 BRANCH 是 main/master)時,「已在主線上」不能當成沒新東西——應退回修正前的空樹+截上線點,或比照 pre-push 用「不在其他遠端分支上的最早提交」取起點;回 None 時補一筆跳過帳。

## F2 doctor 新給的 CI 那步拿掉了空 before 的處理,pull_request 觸發時整步 rc2 變紅
severity: minor
blocking: 否 —— 失敗是大聲的(CI 紅、不是靜默放行),說明行也提到要加 if

引句:「"python3 scripts/lumos note-shape --diff \"${{ github.event.before }}..${{ github.sha }}\""」

修正前 doctor 給的那步有 `case "$B" in 0{40}|"") B=<空樹>`,空的 before 也能跑;修正後命令本身不處理空值,而貼上去的 `- run:` 那行沒有 `if: github.event_name == 'push'`(只寫在下一行的括號說明裡)。消費專案 workflow 若 `on: [push, pull_request]`(常見寫法),pull_request opened 事件的 before 是空字串 → `--diff "..<sha>"` → `_lens_range_ok` 回 None → rc 2 → 該步紅。已實跑:`note-shape --diff ..<sha>` 回 `(2, '擋下:--diff 要給 <起點>..<終點>——恰好兩個點、兩端都要有')`。工具鏈自己的 ci.yml 有補 `[ -n "$BEFORE" ] || BEFORE=000…`,doctor 的那步沒有同步。
修法方向:把 `if: github.event_name == 'push'` 放進貼上的片段本身,或命令裡保留空值→40 個 0 的替換。

最嚴重等級 major,blocking 1 條。
