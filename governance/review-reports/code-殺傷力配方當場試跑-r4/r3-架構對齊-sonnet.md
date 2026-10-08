severity: minor

# 架構對齊-sonnet(另開迴圈第 3 輪,只審 r3-delta)

## 三問

1. 分層與依賴方向:對齊。`_kill_old_issue`/`_kill_new_issue`/`_kill_detail_str`/`_kill_inv_has`/`_kill_covers_list` 都是判法層的小謂詞,聚在 `_kill_judge_file` 正下方,`cmd_guard_kill` 單向往下呼叫;沒有倒灌、沒有跨層直呼。`--json` 與 kill-log 都改走同檔既有的 `_kill_esc`,與 `_kill_rm_show` 同層同做法。對照:file: `scripts/lumos:14172`、file: `scripts/lumos:14196`、file: `scripts/lumos:14225`、file: `scripts/lumos:14799`。
2. 命名與錯誤處理:對齊。`*_issue` 回「說明或空字串」與 `_kill_path_issue`(file: `scripts/lumos:14109`)同形狀同命名,上一輪 F2 的命名與放置問題已修好;`covers` 抽成 `_kill_covers_list` 與 `_kill_detail_str` 同形狀,上一輪「三處各用各的形狀」縮成兩種(輔助函式與 try/except 的 `_kill_inv_has`,後者因要保留 in 的語意可接受)。`_kill_esc` 輸出仍是合法 JSON,讀端(file: `scripts/lumos:7706` gov 第 5 源、file: `scripts/lumos:41531` `_backing_kill_rows` 走的 `_drift_jsonl_rows`)都是 json.loads 讀回,跳脫後的值讀回不變,沒有讀端拿原始文字比對。
3. 第二種做法:`--json` 這條已與 `_kill_rm_show` 合流(file: `scripts/lumos:14799`),上一輪 F1 修好。kill-log 寫入改成「對整行 json.dumps 文字套 `_kill_esc`」,而其他 jsonl 帳本(governance-log file: `scripts/lumos:1228`、`scripts/lumos:1270`,usage-log file: `scripts/lumos:15703`,canary 帳 `_jsonl_append_verified` file: `scripts/lumos:8995`)都是直接 `json.dumps(..., ensure_ascii=False) + "\n"`,所以 kill-log 成了帳本寫法裡唯一多一道跳脫的。見 F1(minor)。

## F1 kill-log 是唯一對整行文字再套 _kill_esc 的帳本寫入,其他帳本寫法不同
severity: minor
blocking: 否
引句:「fh.write(_kill_esc(json.dumps({"ts": ts, "node": rel, "commit": commit,」
file: `scripts/lumos:1228`(governance-log 直接 json.dumps 寫入)、file: `scripts/lumos:8995`(`_jsonl_append_verified` 同樣直接寫)、file: `scripts/lumos:15703`(usage-log 同)
1. 結構上沒有跨層,也沒有行為回歸:跳脫只動 Cc/Cf/Zl/Zp/Cs 字元,換成 \uXXXX 文字,json.loads 讀回同一個值;這是 kill-log 因為欄位是人寫的(invariant、note、tail)才需要,理由在註解裡有寫。
2. 不對齊點:帳本寫入沒有共用寫法,別的帳本若欄位帶落單替身字元,寫入時一樣會因 UTF-8 編碼出錯(governance-log 的 note、canary 的 findings 都是人寫字),專案現在是「kill-log 一本特殊處理」。我判不準這是「該升成共用帳本寫入輔助」還是「只有 kill-log 欄位是不可信提交來的,特殊處理合理」,標 ⚠。給不出別本帳實際會崩的場景,所以只列 minor,不要求這輪處理;若日後第二本帳也需要,抽成共用的 jsonl 寫入輔助即可。

不對齊共 1 條,其中 major 0 條
最高等級:minor,blocking 共 0 條
