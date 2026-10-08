severity: minor

我在 `/tmp/k_r2` 用 `rw` 的 35de50ac 加上舊版 6c22a561 做了對照。圖譜鏡頭見文末。

**K1 配對放寬帳的去重記號檔讀到壞內容時,整筆放寬帳永遠記不進去**
severity: minor
blocking: 否 — 只丟治理帳這一筆,不改檢查判定,而且記號檔要被外力弄壞才會發生。
引句:「seen = mark.read_text(encoding="utf-8").split() if mark.is_file() else []」
1. 輸入:`.git/lumos-relaxed-seen` 含非 UTF-8 位元組,例如 `b"\xff\xfe\x00junk"`。
2. 路徑:`_ns_relaxed_seen` 的 `try` 只接 `OSError`。`UnicodeDecodeError` 屬於 `ValueError`,會一路冒到 `_ns_relaxed_record` 最外層的 `except Exception`。
3. 預期:壞記號檔視為空,照記帳。實際:印「提醒:放寬帳這次沒記成(UnicodeDecodeError)」,`.governance-log.jsonl` 根本沒寫。壞檔不會自己好,之後每次推送的放寬帳都一樣丟。
4. 重現(`/tmp/k_r2/seen.py`):
   - 輸出 `garbage raises UnicodeDecodeError`。
   - 走 `_ns_relaxed_record` 時輸出 `ledger after garbage: False`。
5. 同一個 `try` 對「記號檔是目錄」的處理是對的:輸出 `dir -> False`。

**K2 記號檔是非原子的讀改寫,多個會談同時推送會互相蓋掉**
severity: minor
blocking: 否 — 後果只是同一次推送多記一筆重複的放寬帳。
引句:「mark.write_text("\n".join((seen + [key])[-50:]) + "\n", encoding="utf-8")」
1. `write_text` 先截斷再寫,沒有鎖,也不是「暫存→replace」。同一個 repo 兩個會談同時推送時,後寫的人用舊的 `seen` 覆蓋前一個人的記號。
2. 重現(`/tmp/k_r2/seen2.py`):16 個行程同時各寫一個不同推送編號的記號,連跑三輪。每輪 40 個鍵,最後只剩 39、31、9 個。
3. 後果:自己這次推送的鍵被別人蓋掉後,同一推送的下一條分支又會記一筆。
4. 「只留 50 筆」對單一推送夠用。80 個不同推送併發時,正好剩 50 行,沒有溢出。
5. 另一個小缺口:記號是在 `_gate_event_or_warn` 寫帳之前就寫下去的。第一條分支的帳若寫失敗,同一推送的第二條分支會因為「已記過」而跳過,這筆帳就完全沒有了。

**K3 起點加終點一起批次讀只限檔數,沒限總位元組,峰值記憶體偏高**
severity: minor
blocking: 否 — 只有在剛好卡上限的大推送才會碰到,而且舊版就是這個量級。
引句:「blobs = _nodehome_cat_blobs_capped(repo_root, [f"{base_where}:{b}" for b, _g in cands]」
1. 造了 200 篇、每篇 501 KB 的筆記,起點與終點都各有十對補括號(剛好在 200 篇、兩萬對的上限內),跑 `_notelines_append_pairs`,結果是 200 個配對全成立。
2. 實測:新版 maxrss 532 MB、2.47 秒;舊版(6c22a561)489 MB、1.56 秒。
3. 上限是 200 篇、每篇 512 KB,兩倍就是 400 個 blob 約 200 MB。再加上 `cat-file` 的 stdout 整塊和逐 blob 切片,實際到約 2.6 倍。
4. 新版比舊版多 9% 記憶體、慢約 58%。沒有任何位元組總量上限,只有檔數上限。
5. 附帶的行為差異:終點版本單篇超過 512 KB 現在也不配(舊版 `reader` 不設上限)。方向是偏嚴,可以接受。

**實測沒問題的項目(依派工詞逐項)**
- `_gate_event_fit` 二分:
  - 實測(`/tmp/k_r2/fit.py`、`fit2.py`):

    | 筆數 | 時間 | 峰值記憶體 | 重組次數 | 最終留下 |
    |---|---|---|---|---|
    | 5 千 | 0.06 秒 | 1.7 MB | 14 | 47 筆 |
    | 2 萬 | 0.12 秒 | 6.8 MB | 16 | 47 筆 |
    | 5 萬 | 0.29 秒 | 17 MB | 17 | 47 筆 |

  - 每次重組只序列化前 `mid` 筆,總成本約是整份大小的兩倍,沒有第二個平方成本。
  - `_drift_m1_fit` 同時有 5 萬列和 5 萬個 nodes:1.58 秒、45 MB,nodes 截到 20 並記 `rows_truncated`。
  - 對照:`eq.py` 隨機 300 組輸入,新舊實作的 rows、nodes 和旗標逐項相同,0 筆差異。
- 被刪摘要行改走 `_notelines_parse_hunks`:
  - 造了 1500 篇、89 萬行的大 diff(`/tmp/k_r2/huge`)。
  - 新版 2.05 秒,舊版 0.91 秒。
  - tracemalloc 下峰值 344 MB,舊版 237 MB。多出來的是多解析一遍,量級可接受。
  - 被刪檔(`+++ /dev/null`)的刪除行仍會留在 `segs`,不會漏。
- `_ns_append_nfc_clash` 多一次解析:同一個 diff 約 0.8 秒(`parse_hunks` 本身 0.90 秒),候選超限就整批不配,不是失敗。
- 沒有違規或沒有送審項目時的配對成本:
  - `_ns_append_subtract` 只在 `pv` 非空時呼叫 `pairs.table()`。
  - `_note_audit_mark_appended` 開頭有 `if not items: return`。
  - 否定現況句提醒走 `_ns_negation_hints`,只在該行有命中時才呼叫 `pairs.table()`。這是設計內的延遲算法,所以只有有命中的推送才付配對成本,最壞情況就是 K3 的量。

**圖譜鏡頭(逐條判)**
- `reversibility-governance-ledger`(只有 RISK、沒內容)、`pitfalls-code-loop`(同)、`lumos-cli-read`、`bound-tests-gate`、`guard-kill`、`design-loop`:這份 diff 沒碰 search 濾網、固定席測試的執行、guard kill 的 rc 與 JSON、處置閘,所以不影響。
- `授權與歸屬`:`scripts/lumos` 的 SPDX 與 MIT 檔頭不在這份 diff 裡。`scripts/templates/note-audit-judge.md` 只改了內文,第 1、2 行的 SPDX 兩行還在,所以不影響。
- `測試假綠形態`:要求修 bug 的測試配前置斷言。這份 patch 只含 `scripts/lumos` 與範本,沒有 `scripts/test_lumos.py`。我看不到新增的測試,所以那一條判不了。

最高嚴重度 minor,blocking 0 條
