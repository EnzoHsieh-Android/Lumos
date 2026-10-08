severity: minor

# 回頭重讀 代碼審 r1 併發與資源席(sonnet)

量測環境:`git clone --shared` 的 94e28375,macOS,`/opt/homebrew/bin/python3`(3.14),圖譜約 75 篇 Systems、2333 個提交。

## F1 30 秒軟上限管不到「讀頂端圖譜」那一大段,git 變慢時實際遠超過 30 秒;連沒改任何程式的推送也付整段費用
severity: minor
blocking: 否
引句:「截止時間是軟的:只在這裡的呼叫點之間看;共用函式內部不收,單次 git 仍是它們自己的上限。」
file: `scripts/lumos:24198`(_nodehome_clamp_base 所在區段;_nodehome_side 逐篇 git show、內部沒收 deadline)

1. 正常速度下沒問題:reread-check 整段 1.7 到 4.6 秒(範圍 1 到 2000 個提交都一樣,約 91 到 112 次 git 呼叫,最大常駐記憶體 195 MB,與 `lumos --version` 基線 197 MB 相同,沒有額外記憶體成本)。對照 drift check 約 1.3 秒、home check 約 6.2 秒。
2. 但呼叫次數跟圖譜篇數成正比,不跟範圍大小走:`HEAD~1..HEAD~1`(空範圍)也是 91 次 git(其中約 76 次是 `git show <sha>:<筆記>`,來自 `_note_reread_scan` → `_nodehome_side` 讀頂端每篇筆記)。所以只改文件、或根本沒改程式的推送也付這筆;範圍裡沒有程式檔時可以在 `_nodehome_side` 之前就回「沒有候選」。
3. deadline 只在 `_note_reread_scan` 的幾個 `_tick()` 之間檢查,`_nodehome_side` 那 70 幾次呼叫中間不看。重現(在 clone 裡,用一支會睡眠的 git 包裝腳本放進 PATH,每次 git 呼叫前睡 N 秒):
   - `SLOWGIT=0.5 lumos note-audit reread-check --diff HEAD~30..HEAD~1` → 印「這次沒提醒:逾時(超過 30 秒)」,但實際耗時 48 秒(87 次 git)。
   - `SLOWGIT=1.5` → 實際耗時 134 秒,也就是上限的 4.5 倍,而且是把整段跑完才發現逾時。
   掛鉤註解寫「最多約 30 秒(工具自己的軟上限)」,掛鉤自己沒有外層逾時(macOS 沒有 timeout 指令)。圖譜到幾百篇、或 Windows 殺毒軟體讓每次 git 變 0.1 秒以上時,這段就會超過 30 秒,再乘上逐 ref 各跑一次。
4. 嚴重度降成 minor:重現用的是人為放慢的 git,正常機器不觸發,而且只提醒、結果恆放行;只是註解與計劃宣稱的 30 秒不是真上限。建議:把 deadline 傳進 `_nodehome_side` 的逐篇讀取(比照 `_notes_status_flipped` 的 deadline 做法),或在 `_note_reread_scan` 先看 `changed` 有沒有程式檔、沒有就提早回;注意該函式與原有的 home check 共用,改動要留意 strict 語意。

## 已驗證沒問題(不計 finding)
- Ctrl-C:對 `reread-check` 程序在 1.0、3.0、5.5 秒各送一次 SIGINT(慢 git 下),三次都是被 SIGINT 終止(Python returncode -2,shell 視為 130),沒有被 `except Exception` 吞掉,沒有留下 git 子程序、`.git/*.lock`。掛鉤只對 130 停下的設計成立。
- 其他訊號:SIGTERM 得 143、SIGHUP 得 129,掛鉤走「照推」分支,跟註解寫的一致(OOM 的 137 同理)。
- 暫存檔與原子寫入:項目檔與紀錄檔都走 `_write_lf`(唯一暫存名、O_EXCL、`os.replace`;例外時清掉);項目檔名是 `reread-<材料指紋>-<編排者>.md`,兩個會談同時 prepare 同一份材料會寫出位元組相同的檔,原子替換不互踩;record 檔名帶 32 位亂數,兩個會談同時 record 不會撞名(只會多出兩份同對照指紋的紀錄,check 只比指紋集合,無害)。
- 治理帳:`_gate_event` 是單次 append。最壞的一筆(候選 53 篇、nodes 與 note 各列 50 項)實測 8573 位元組,超過 8192 緩衝;另以 8 個程序各 300 次、每筆約 9 KB 同時 append 同一檔,2400 行全數可解析、無交錯。
- 目錄沒有資料夾(`governance/reread-verdicts/` 不存在)是空集合而不是 git 失敗,不會自鎖;新增資料夾由 record 的 `mkdir(parents=True, exist_ok=True)` 處理,兩會談同時 mkdir 安全。

最高等級:minor
