severity: major

## F1 coverage 讀 HEAD 的設定，技能文件卻要人在補完對照表、還沒提交時就跑它
severity: major
blocking: 是
引句:「設定讀 HEAD 提交的樹(跟推送前判定讀的是同一份);」
佐證: `scripts/lumos:41161`（`_e2e_select_cmd` 的 `--changed` 讀工作目錄設定 `_e2e_worktree_e2e`）

技能文件新增的步驟是：「`lumos macrobench --check-config` 回 0 才算接好；再跑 `lumos android-e2e coverage --changed`」。這一步緊接在「新增功能或使用情境時一起補（同一個提交）」之後，所以照做的人還沒提交。計劃條款 S6 也要求「補進對照表後再跑應不再列」。

1. 輸入：已提交 `app/src/main/Z.kt`，Z.kt 不在任何功能的 paths 裡。接著在工作目錄把 `login.paths` 加上 Z.kt，不提交。
2. 執行路徑：`_e2e_coverage_input` 呼叫 `_e2e_config_at(root, head)`，讀的是 HEAD 提交樹裡的 macrobench.json，看不到工作目錄的修改。
3. 實測：補表後再跑 `coverage --changed`，rc 0，仍印「沒歸屬的程式檔：1 支 / app/src/main/ 沒歸屬 1 支」。同一狀態下 `android-e2e select --changed` 已經挑到 `login.ok`。
4. 另一個極端：專案原本沒有 `e2e.features`、人正要新補。這時 `coverage` 讀到 HEAD 沒有 features，擋下並回 2（訊息是「e2e 段沒有 features」或「HEAD 的 macrobench.json 沒有 e2e 段」）。
5. 結果：技能文件寫的操作順序會讓人看到過期的報告，或被擋下，以為對照表沒補成功。S6 的驗收條款在未提交時也不成立。
6. 測試沒覆蓋：五支新測試都先提交設定再跑。沒有一條測「工作目錄改了設定、未提交」，所以把讀取來源改壞，測試照綠。
7. 修法二選一：`--changed` 時改讀工作目錄設定，和 `select --changed` 一致；或在技能文件與 README 明說要先提交再跑。

我用 `test_lumos.py` 的 `_e2eg_proj`、`_e2e_set_cfg` 做了暫存專案重現，結果如上。重現用的暫存目錄已刪。

## F2 涵蓋報告的「有會判情境」判準少測 visual 與 stability 兩個鍵
severity: minor
blocking: 否
引句:「if not any(c.get(k) for c in v["cases"].values() for k in ("flows", "visual", "stability")))」
佐證: `scripts/lumos:41579`（推送前判定用同一組三個鍵分「需驗」和「只列效能」）

具體改壞：把 `"visual"` 或 `"stability"` 從元組拿掉。只有 visual 或 stability 的功能會被誤報成「沒有會判情境的功能」，報告和推送前判定就不一致。

`t_android_e2e_coverage_cases_and_materials` 只有 flows 情境和 macrobench-only 情境，所以這種改壞測試照綠。這個報告的用意就是和推送前判定同口徑，這個口徑沒有被測試守住，屬覆蓋面不足，所以標 minor。

## F3 報告把 shared_paths 內的檔當成「有歸屬」，但推送判定一樣要求整套跑
severity: minor
blocking: 否
引句:「if not any(_e2e_under(f, d) for d in shared) and not _e2e_owners(f, feats, index):」

輸入：檔案同時在某功能 paths 和 shared_paths 底下。推送判定（`_e2e_gate_owners`）先檢查 shared，歸類為「共用程式，要整套」。報告則先檢查 shared 就當作已處理，不列出。

因此報告印的「沒歸屬 N 支（改到它們時，推送前檢查會要求整套跑）」是推送判定要求整套的檔的子集，不是全集。若要說明這個口徑，文件裡一句話就夠，行為本身不算錯，所以只標 minor。

## manifest 逐題判定
- py-eventloop、py-parallel：誤報。新程式全是同步 CLI，沒有 async。
- py-external：誤報。新增程式只呼叫本地 git，且有 timeout（doctor 用 10 秒，預設 20 秒）。
- py-memory：誤報。報告在記憶體裡只建一次索引和分組，規模與檔數呈線性。
- py-hotpath：誤報。逐檔查歸屬用 `_e2e_owner_index` 加上 `_e2e_prefixes` 限深，沒有平方工作量。`shared` 逐項比對上限 200 項，已有 `E2E_PATH_LIST_MAX` 保護。
- 鎖與交易類題目：範圍外，標誤報。
- ruff：新增行我看不出新告警，沒有跑 ruff 實測。

## 其他逐項檢查結果
- 邊界：`app/` 與 `app2/` 前綴，`_e2e_under` 用整段比對，沒問題。exclude 與 shared 同時命中的檔，`_e2e_scope_hit` 先排除，和推送判定一致。
- 例外與 None：`ls-tree` 失敗、逾時、git 回 None 都轉成 rc2 擋下。doctor 路徑吞掉 OSError、ValueError、KeyError、TypeError，沒有崩潰路徑。
- 唯讀、冪等：不寫檔，重跑結果相同。
- 產圖腳本：`python3.14 assets/readme-diagrams/generate.py --check` 回報 26 張 SVG 驗證通過且可重現。
- 文件旗標：README、技能文件的旗標名（`--changed`、`--files`、`--json`）和 rc 與程式一致。唯一對不上的是 F1 的「補完先跑」時序。
- 測試品質：S1 到 S5 用真子程序跑 CLI，並檢查輸出，不是結構檢查。缺口只有 F1 和 F2。

## 圖譜固定席
- lumos-cli-read、guard-kill、lumos-cli-lifecycle、design-loop 的 ★INVARIANT★：不影響。diff 沒碰 search 過濾、guard kill 的 rc 或 JSON、re-inject 或 design-loop 處置閘。新子命令獨立，只透過 `_say_block` 輸出。
- 測試假綠形態：不影響其「還原翻紅釘」條款。新測試不是修 bug 的還原釘，但 F2 屬同族的「改壞仍綠」。
- pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger：不影響。命令唯讀，不寫治理帳，不動 pitfalls 或收斂記帳流程。`generate.py` 的改動只是圖內容，`--check` 通過。
- android-e2e 的 `_say_block` 單一出口：新代碼沒有自己印「擋下：」，符合；唯一外來文字回顯屬範圍外。

總結:本報告最高等級為 major
