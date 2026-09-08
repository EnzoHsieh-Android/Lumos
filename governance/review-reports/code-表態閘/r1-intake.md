# r1 intake — code-表態閘(2026-09-09 凌晨;tier high;五席 sonnet + Gemini 備援 + Codex 兩席(03:48 用量重置後補跑))

preflight-4: ran(代碼審首輪;材料=r1-snapshot.patch 1644 行(U6,scripts/lumos+pre-push+impact-hook+ci.yml)、r1-snapshot-tests.patch 455 行;refcheck 六份報告 file:line 全對得上;quote-check:正確性/邊界/併發資源/架構對齊全錨,合約測試席 4 句錨在測試 patch(對 r1-snapshot-tests.patch 跑 quote-check 全錨),Gemini 1/2 錨不到——備援席不算否決票)

## 收貨:編排者機械重現(命令+結果;HIT=現象重現、判準另驗)
- 邊界 f1(blocker)evidence `10-5`/`5-0` → HIT:`_validate_repo_ref(<repo>, "five.txt", "10-5", at_sha=<sha>)` 在修前 IndexError、`5-0` 回 ok;外層 `except Exception` 吞成 fail-open。判準同意:形狀壞應在寫側 rc2,核對時任何例外應擋不放行。折:`_dispositions_split_path_line` 驗 lo≥1、a≤b;`_validate_repo_ref` 兩條路加 `hi<lo or lo>len`;`_dispositions_verdict` 每題包例外→「無法驗證」擋。釘:t_codeloop_dispositions_r1_folds ①。
- 正確性 f1(blocker)壞 platforms 設定 → HIT:兩平台無 default_platform 的合法 JSON,`code-loop check` 修前 rc0 ✅;修後 rc1「platforms 不合法」。釘:同測試 ②。
- 正確性 f2(major)dispositions 對同一設定 traceback → HIT(修前 ValueError 穿出 main);折:try→rc2。釘:②。
- 正確性 f3(major)鏡頭 todo 缺 issue TypeError → HIT(`None + " "`);折:全 str(… or "")。釘:⑦。
- 正確性 f4/f5/f6(minor)訊息與樣板 high-only → HIT(讀碼);折:pre-push 逃生文案按原因分三路;check 紅+擋的是表態時不印 skip 提示;樣板 high-only 且 tier≠high 印 {}。釘:⑤。
- 邊界 f2(major)/合約測試 f3(major)bound-tests-gate 節點沒跟上 → HIT(筆記第 41 行仍寫「直接呼叫 bound-tests --advisory」);折:KEY 補一行、怎麼跑段改寫。判準訂正:★INVARIANT★ 本身(高風險紅→擋)沒被推翻,是外層接線敘事過時。
- 邊界 f3(minor)`--branch ""` → HIT;折:rc2。釘:range_and_branch ③。
- 併發資源 f1(major)`_write_lf` 固定暫存名互搶 → HIT(讀碼:`.tmp-wlf` 固定名);折:marker 用 mkstemp 唯一暫存名。
- 併發資源 f2(major)git 子程序無 timeout → HIT(讀碼);折:`LUMOS_DISP_GIT_TIMEOUT`(預設 8 秒)套 cat-file/show/grep/merge-base/diff,超時=該題無法驗證擋下。釘:③(假 git 對 show 睡 2 秒、上限 0.3 秒 → rc1「無法驗證」)。
- 併發資源 f3 / 合約測試 f1 / Gemini f1(major,三席獨立一致)同 sha 重表態 ts 相同去重折成一筆 → HIT:兩次 dispositions 治理帳 ts 皆 HEAD commit 時間。折:事件加 `written_at`(微秒),mapper 鑑別子改拿它。釘:⑥(真走 CLI 寫兩次 → gov --stats「做到了 1、不適用 1」)。
- 併發資源 f4(minor)marker 壞掉判「沒表態」→ HIT;折:壞掉退治理帳。釘:④。
- 併發資源 f5(minor)marker 寫失敗 traceback → HIT;折:try→提醒、rc0(治理帳是真相)。
- 併發資源 f6(minor)鏡頭每次掃治理帳 → HIT(18 ms/次,帳會長);折:鏡頭 marker_only。
- 併發資源 f7(minor)暖機行程重算 key → HIT(讀碼);折:派工那一刻的 key 走環境變數 LUMOS_LENS_DISP_KEY 給背景行程。
- 合約測試 f2(major)③ 沒測到跨分支讀取 → HIT(席位用副本證明拿掉讀取仍 6/6 綠;我重讀後同意:main checkout 下 merge-base 短路成零適用題);折:③ 改在 feat/disp 上寫 release 名下、check --branch release 放行且 checked=1、--branch other 擋。
- 合約測試 f4(minor)只有 kt 有直接樣本 → HIT;折:cs/sql/swift/node/vue 各一題命中/不命中。
- 合約測試 f5(minor)docstring 編號 → HIT;折:改 ⑥。
- 架構對齊 f1(major)`_codeloop_record_valid` 沒接進 pass/skip 路徑 → HIT(grep 只兩處);折:guard verdict 步驟 4 改呼叫它。-k bound/codeloop 全綠。
- 架構對齊 f2(major)`_stack_changed_ok` 與 claims 內聯過濾兩份 → HIT;折:claims 改呼叫它、註解搬進 docstring。-k pitfalls 全綠。
- 架構對齊 f3(minor)三種前綴 → HIT;折:校驗/切分/核對 7 支改 `_dispositions_*`,讀寫層留 `_codeloop_*dispositions`(同 `_codeloop_write/_read` 家族),Systems 節點寫明兩族。
- 架構對齊 f4(minor)治理帳失敗硬擋 vs pass/skip 靜默 → HIT;折:刻意,理由寫進 Systems 節點(standard 沒有 pass 事件、治理帳是 CI 讀表態的唯一路徑)。
- Gemini f2(minor)行尾註解 → HIT;折:`_stack_norm_line` 剝行尾 // # -- 與 /* */。釘:t_stack_question_triggers ③。
- pitfalls manifest 1 條(open( 無 with?)→ 邊界席判誤報,我同意:該行在 with 裡。

## 處置
- 全折(code 迴圈任一席 ≥major 則 accepted 必空);refuted 0。
- 外家 Codex 兩席:見下方補記。

## 外家 Codex 兩席補記(03:49 用量重置後補跑;finder gpt-6-astra xhigh、否決 gpt-5.6-terra xhigh;讀的是同一份凍結 patch 與未動的主工作區)
- F1(major)反向行號 → 同 邊界 f1,已折(finder 重現 R1 翻紅屬實)。
- F2 / V1(major)整檔刪除 `+++ /dev/null` 刪行漏掃 → HIT:`git rm app/Screen.kt` 後 pitfalls --diff 修前 applicable {};折:解析器記 `--- a/` 名、`+++ /dev/null` 時用它。釘:t_codeloop_dispositions_r1_folds ⑧。
- F3(major)治理帳的 evidence 字串冒充已提交測試 → HIT:未追蹤 test_untracked + 表態後 commit 治理帳,修前 check 放行;折:git grep 限該 profile 測試副檔名(:(glob)**/*.py 等)並排除 docs/ governance/。釘:⑨。
- F4 / V3(major)advisory 放過高風險紅測試 → HIT(判準同意:旗標只准低風險);折:check 自己算出 high 就硬跑一次(advisory=False)照擋;advisory 也傳進 _bound_tests_check(否決 V3:不傳會對低風險跑整套 600 秒);pre-push 對 pitfalls 空輸出不帶旗標。釘:⑪(替身:red+passed+high,帶旗標仍擋、呼叫序 [True, False])。
- F5 / V2(major)推非 checkout 分支表態綁錯 sha → HIT(判準同意);折:dispositions 加 --at-sha(驗 commit 存在、ts 取該版本),BLOCKED 訊息帶 --at-sha。釘:⑩。
- F6 / V4(minor)ts 去重 → 同 併發 f3,已折(written_at)。
- F7(minor)字串剝除弄啞三題 → HIT:`socket.on("error"` / `LIKE '%foo'` / `from "./x"` 實跑;折:spec 加 raw 旗標、_STACK_TRIGGERS 第三欄、_stack_applicability 對 raw 題用只剝註解的行。釘:⑫。
- F8(minor)鏡頭措辭「已驗證據存在」不實 → HIT;折:改「寫入時只驗形狀,推送前才驗證據存在」。
- 兩席 pitfalls manifest 判誤報,同意。quote-check:finder 8 句全錨;否決 4 句全錨。
- ★觀察★:五席同門各守一鏡頭,外家兩席抓到的 5 條全是「路徑組合」型(刪檔 diff 形狀 × 解析器;帳本字串 × grep 範圍;pitfalls 空輸出 × 旗標;checkout ≠ 被推 × 座標)——同門席沒一個抓到。

## 處置(最終)
- 五席 sonnet 25 條 + Gemini 2 條 + Codex finder 8 條 + 否決 4 條 = 39 條(去掉跨席重複後 ~31 個獨立問題),全折、accepted 空、refuted none。
- 全套測試:折入後 4797 綠(sonnet 輪)、Codex 折入後見 fullsuite-branch3(記帳時補數字)。
