# 回頭條件消失式與生來成立 r2 收貨

席位:通才 8(U1–U8)、正確性 9(C1–C9)、邊界輸入 10(B1–B10)、架構對齊 5(Z1–Z5);共 32 條,blocking 6(U1、C1、C2、B1、B2、B3)。正確性、邊界輸入兩席引句全錨;架構對齊席 #5(Z5)與通才席 #8(U8)各一句是近似引用(前者省略中間「點名讀不出的檔、」、後者去掉原文「條件寫錯」外的「」),錨不到——不改席位引句,編排者對凍結快照機械重現(見重現表),照採。四席交齊才動計劃。

## 依根因分組(全部折)

1. 讀位元組(U1、C2、B1)→ 另存位元組快取、同一次批次讀;NUL、LFS、不是嚴格 UTF-8 一律判不了;天花板 7。
2. 往回查的歷史(C1、U6、B10、C3、C4、B2、B5)→ 只沿主幹;同一篇兩行條件一樣、某一版讀不出或太大或非 UTF-8、partial clone 一律判不了;總量上限;側分支、改名寫進天花板 2;標記拿掉「從沒提醒過」。
3. 拆值與讀鍵的地方(B3、C6、Z5、C7、B6、U8)→ 逐一列出十處;`_drift_cond_split(v, k)`;`_slot_retire_err` 與 REVISIT 寫法要求一致;反引號檢查放在看原文的呼叫端。
4. git 呼叫(B4、C5、U2、U5、Z1、Z2)→ `_lens_git` 帶逾時、`-c core.quotePath=false`、`:(literal)`、原樣路徑。
5. 資源(C9、U7、B9)→ 最多 20 條、每個提交的樹與圖譜判完就丟。
6. 列鍵文件(C8、B7、U4)→ 補 reference.md、SKILL.md、範本列鍵那句;守衛測試掃這些文件。
7. 呈現與點名(Z3、Z4、U3)→ 判不了照 `_drift_bad_note` 點名;born 照 `_drift_prev_ack_line` 另起 `_drift_born_line`;呼叫點在 `cmd_drift_scan`。
8. 路徑找不到的點名原因(B8)→ 點名多一句「路徑在這一版就找不到」。

## 重現表

| id | 怎麼查 | 結果 | 去向 |
|---|---|---|---|
| U1 | 讀 `_DriftProbeTree._read` 用替代字元解碼存文字 | HIT | 折(第 1 組) |
| U2 | 讀 `_nodehome_git` 沒有逾時參數、沒有 `-c` | HIT | 折(第 4 組) |
| U3 | 讀 `_drift_bad_note` 與 scan 的判不了寫入點 | HIT | 折(第 7 組) |
| U4 | `grep -n "when-status" skills/lumos-project-notes/*.md` 列鍵處 | HIT | 折(第 6 組) |
| U5 | 讀 repo 其他 git log 呼叫釘 `:(literal)` | HIT | 折(第 4 組) |
| U6 | 同 C1 | HIT | 折(第 2 組) |
| U7 | 同 C9 | HIT | 折(第 5 組) |
| U8 | 引句近似錨不到;機械重現:`grep -n 之後同一個標記內出現反引號 r2-snapshot.md` 命中〈做法〉1.1,共用解析器 `_probe_parse` 收到的是 `_strip_inline_markup` 剝過的文字 | HIT | 折(第 3 組) |
| C1 | 席位在 /tmp/revisitB-r2/exp/m 實跑:自動合併提交讓 git log 版本交錯 | HIT | 折(第 2 組) |
| C2 | 同 U1(Big5 例) | HIT | 折(第 1 組) |
| C3 | 讀計劃「同一條」只比條件標記,同篇兩行相同 | HIT | 折(第 2 組) |
| C4 | 讀 `_nodehome_cat_blobs_capped` 的 None 三種意思 | HIT | 折(第 2 組) |
| C5 | 同 U2;席位實測檔名含 `[` 時混進別篇提交 | HIT | 折(第 4 組) |
| C6 | `grep -n '_drift_cond_split(\|rsplit("::", 1)'` 只有 4 處呼叫、另 3 處自己切 | HIT | 折(第 3 組) |
| C7 | 讀計劃 1.4 與 S4 | HIT | 折(第 3 組) |
| C8 | 讀 `scripts/templates/graph-discipline.md`、`skills/lumos-project-notes/reference.md` 列四個鍵 | HIT | 折(第 6 組) |
| C9 | 讀 `_DriftProbeTree.corpus` 每版讀全語料、列樹快取上限 8 | HIT | 折(第 5 組) |
| B1 | 同 U1(席位實跑 Big5) | HIT | 折(第 1 組) |
| B2 | 同 C4 | HIT | 折(第 2 組) |
| B3 | 同 C6 | HIT | 折(第 3 組) |
| B4 | 同 U2 | HIT | 折(第 4 組) |
| B5 | 席位實測 partial clone 下 cat-file 讀舊 blob 會連網 | HIT | 折(第 2 組) |
| B6 | 讀 `_slot_retire_err` 對 when-* 的檢查與 REVISIT 那條路不同 | HIT | 折(第 3 組) |
| B7 | 同 C8 | HIT | 折(第 6 組) |
| B8 | 讀 `_drift_probe_judge` 新寫已成立的原因句 | HIT | 折(第 8 組) |
| B9 | 同 C9 | HIT | 折(第 5 組) |
| B10 | 同 C1(改名、拆篇部分寫進天花板) | HIT | 折(第 2 組) |
| Z1 | 同 U2 | HIT | 折(第 4 組) |
| Z2 | 讀 `_nodehome_list` 回 NFC 路徑、原樣路徑在另一份 | HIT | 折(第 4 組) |
| Z3 | 同 U3 | HIT | 折(第 7 組) |
| Z4 | 讀 `_drift_prev_ack_line` 的呈現 | HIT | 折(第 7 組) |
| Z5 | 引句近似錨不到;機械重現:`grep -n 值驗證全部呼叫它 r2-snapshot.md` 命中〈做法〉1.1,實際呼叫 `_drift_cond_split` 的只有 4 處(同 C6) | HIT | 折(第 3 組) |
