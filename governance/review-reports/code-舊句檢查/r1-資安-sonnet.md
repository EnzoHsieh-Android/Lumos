severity: major

# 資安席(sonnet)r1:舊句檢查 m1

審材:r1-snapshot-code.patch 為主,tests 部分只看有沒有寫髒真家目錄。實驗都在 `git clone --shared` 出來的臨時目錄、HOME 換成假目錄跑。

## F1 名稱正則沒有時間上限,推送內容能讓 drift check 卡死(30 秒上限擋不住)
severity: major
blocking: 是
引句:「        toks = sorted({m.group(0) for m in rx.finditer(ln) if not _drift_m1_clause_hist(ln, m.start())})」
佐證行:file: `scripts/lumos:_drift_m1_name_rx`(patch 內 `return re.compile("|".join(parts)) if parts else None`);截止時間只在 `_drift_m1_scan_note` 每 200 行與每篇筆記之間檢查。
敘述:
1. 攻擊者(投稿者)的一個提交同時做兩件事:刪掉一支有 3 萬個函式的 py 檔(起點有、終點沒有,全過形狀過濾成為候選),並在筆記裡寫一段「(已移除 gen_func_000000 gen_func_000001 …)」讓先篩(_drift_m1_prefilter,只擋 ASCII 詞不在圖譜全文的名稱)放行全部名稱,同一篇再放一行約 200 KB、沒有命中的長行。
2. `_drift_m1_name_rx` 把幾萬個名稱編成一條 `|` 分支正則,Python 的 re 對每個位置逐分支試,`rx.finditer(ln)` 掃一條長行是一次不可中斷的呼叫;`check_time()` 只在行與行之間看,所以 `_DRIFT_M1_BUDGET_SEC = 30` 管不到這一步。
3. 重現(乾淨 clone,HOME 換假的):base 提交放 `src/gen.py`(30000 個 `def gen_func_NNNNNN(): pass`)加 `docs/kg-knowledge/Systems/A.md`(about_code 列 src/gen.py);下一提交刪 gen.py、A.md 正文寫 `(已移除 ` + 3 萬個名稱 + `)`,再一行 3 萬個 `abcN` 詞。跑 `python3 scripts/lumos drift check --diff <base>..HEAD`:
   - 3000 個名稱、約 15 KB 長行:real 6.7 秒(已超線性);
   - 3 萬個名稱、約 200 KB 長行:跑了 5 分 35 秒 CPU 仍未結束,我手動殺掉(預算 30 秒)。
4. 後果:pre-push 掛鉤與 CI 的 drift check 都會走到這裡(範圍裡有改到程式檔就跑),被推送內容拖死;`timeout` 狀態、帳、結論行全不會出現,別人的推送被卡住。沒有 candidates 數量上限,也沒有單行長度上限。

## F2 名稱過濾漏了 U+2028/U+2029,列出來的表態指令貼上去會被 ack 擋回,block 模式下這筆永遠處理不掉
severity: minor
blocking: 否
引句:「    return 1 <= len(s) <= _DRIFT_M1_NAME_MAX and _esc_clean(name, 10 ** 6) == name」
佐證行:file: `scripts/lumos:_drift_one_line`(ack 側用 splitlines 語意擋 U+2028/2029)、`scripts/lumos:_esc_clean`(只換 C0 與 0x7f–0x9f,U+2028 與雙向控制字元 U+202E 原樣通過)。
敘述:
1. 旗標名稱來自 `add_argument("--foo bar")` 這類任意字串常數;筆記裡寫同樣字串。
2. 重現:`m._drift_m1_name_ok("--foo bar")` 回 True;`m._drift_ack_names_err("m1", ["--foo bar"])` 回 `--name 每個都要去頭尾空白後 1 到 200 字、一行(這個不行:…)`。也就是 drift check 印「照貼就能表態」的指令,貼上去 rc 2。block 模式下這一筆只能改筆記或整批 `LUMOS_SKIP_DRIFT_CHECK=1`。
3. 同一個缺口讓 U+202E(雙向覆寫)照樣印進終端與提示:`_drift_fix_hint("m1",…,["--a‮b"])` 的輸出原樣帶著 U+202E。這是既有 `_esc_clean` 的範圍,m1 新增的是「不帶控制字元才列」這句宣稱靠它判,判準比 ack 側鬆。
4. 沒有 shell 注入:`x';id;'`、`$(…)`、`;`、空白、`--restore` 走 `_drift_sh` 都是整段單引號包住(實跑:輸出 `'--name=x'"'"';id;'"'"''`)。

## 其他角度的結論(不算 finding)
- 文字抽定義正則(`_DRIFT_M1_TEXT_DEF_RE`、`_DRIFT_M1_TEXT_FLAG_RE`、`_DRIFT_M1_QUOTED_FLAG_RE`):逐個看過,錨在行首或固定字面前綴,回溯是線性,沒有災難性回溯;`_DRIFT_M1_HIST_RX` 是字面分支加整字邊界,也線性。
- 快取 `~/.cache/lumos/drift-defs/`:鍵是 git blob 內容編號加 schema 與 Python 版本,讀取端走 `_lens_cache_read`(必須自己 uid、group/other 不可寫、TTL 內、不跟符號連結的目錄由 `_trusted_private_dir` 逐層擋);別的使用者或別的 repo 放不進假定義(內容編號相同就是同一份內容),同帳號的搶跑是既有檔頭已明講的邊界,不算新洞。
- 漏記痕跡 `ledger-miss.jsonl`:目錄同樣過 `_mkdir_trusted_under_home` 與 `_trusted_private_dir`,檔用 `O_NOFOLLOW`、0600 開,沒看到可利用處。
- 寫進治理帳的 rows、nodes 都過 `_esc_clean`;`text_defs_paths` 是原始路徑但經 JSON 轉義寫檔,沒找到會直接印到終端的讀取端,不報。
- tests:m1 測試一律經 `_M1Home` 或 `env={"HOME":…}` 換掉 HOME;我用假 HOME 跑完整組 `-k drift`(709 案例全過),假家目錄底下沒有任何檔被寫,真的 `~/.cache/lumos/drift-defs` 也沒被建。沒有寫髒真快取。

## 圖譜鏡頭逐條判定
- Systems/lumos-cli-read(★INVARIANT★ search 預設排除 superseded):diff 不碰 search 路徑,不影響。
- Systems/bound-tests-gate(★INVARIANT★ 綁定測試真跑):diff 不碰 code-loop check 與綁定測試跑法,不影響。
- Systems/guard-kill(rc 優先序、--json 純度):不碰 guard kill,不影響。
- Systems/授權與歸屬(授權檔不得入 _VENDORED_TOOLKIT;主程式檔頭 SPDX 與 MIT):diff 不動白名單也不動檔頭,不影響。
- Systems/測試假綠形態(還原翻紅釘要有前置斷言):新測試多數附前置斷言;本席不做覆蓋度判定,不影響安全面。
- Systems/lumos-cli-lifecycle(re-inject 保留 sentinel 之外內容):不碰,不影響。
- Systems/design-loop(處置閘第五步):不碰,不影響。
- Systems/pitfalls-code-loop(★RISK★):不碰,不影響。
- 「超出上限只列名」的其餘節點:資安面上只有共用快取寫入器 `_home_cache_write` 由 `_lens_cache_write` 抽出,行為(逐層建、逐層驗、mkstemp、chmod 0600、os.replace)與抽出前一致,只多了回傳 bool,派工鏡頭快取不受影響。

最高等級:major
