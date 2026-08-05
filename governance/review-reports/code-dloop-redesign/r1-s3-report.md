# Code Review 報告：design-loop 重設計 T1-T7 落地（r1-s3）

審查對象：`/private/tmp/claude-501/.../scratchpad/codeloop/code-dloop-redesign-r1-s3.patch`
交叉核對：`/Users/enzo/harness/lumos-toolchain`（真代碼 + git object 資料庫）

---

## Finding 1（blocker）—— diff 本身含一段偽造/損毀的 hunk，不對應任何真實變更

**file:line**：`scripts/lumos`（診斷於 patch 檔 line 844 起的 hunk；宣稱插入位置在 `_refcheck_scan` 之後、`ANCHOR_FILES` 之前）

**引句（逐字複製自 diff 檔）**：
「`@@ -7950,8 +8045,17 @@ def _refcheck_scan(text, repo_root):`」
「`+def _quote_coverage(report_path, spec_path):`」
「`+    n_ok = sum(1 for r in rows if r["ok"])`」

**判定過程（機械可重現，非臆測）**：

1. diff 的 `scripts/lumos` 段宣稱 `index 91d0113..15c3d69`。用 `git cat-file -p` 把這兩顆 blob 從本 repo 的 git object 資料庫真的挖出來（兩顆都存在，非虛構 hash）：
   - `91d0113`（before）：不含 `_quote_coverage`。
   - `15c3d69`（after）：不含 `_quote_coverage`。
   - 且 `git hash-object scripts/lumos`（工作樹現檔）＝`15c3d69e7195...`，與 diff 宣稱的 after-hash 完全吻合，證明「現在 repo 的真狀態」就是這顆 after blob，不是我核對錯資料。
2. 直接對兩顆 blob 跑 `diff -u before after`（真實的、由 git 算出來的差異，不經過人手），逐行核對後：真差異裡完全沒有 `_quote_coverage`——只有 `_quote_norm` / `_quote_rows` / `_loop_status_disposal` / `cmd_quote_check` 等（這些都與投稿 diff 一致，予以採信）。
3. 對整份 patch 檔的**所有 hunk**（不只 scripts/lumos）寫小工具核對 `@@ -a,b +c,d @@` 宣稱的行數是否等於該 hunk 實際的 context/+/- 行數——這是 unified diff 格式的基本不變量，真的 `git diff` 輸出必然滿足。全檔僅有 **一個** hunk 违反：
   ```
   @@ -7950,8 +8045,17 @@ def _refcheck_scan(text, repo_root):
   ```
   宣稱 old-side 8 行、new-side 17 行；實際數出來 old-side 只有 7 行、new-side 只有 15 行——**恰好就是包住 `_quote_coverage` 那一段**。用 `git apply` 對照真的 before blob 試套用，在此 hunk 之後立刻報 `error: corrupt patch`，與手算結果一致。

**結論**：`_quote_coverage` 這個函式（含它的 docstring／實作）在 diff 檔裡看起來像一段正常的新增程式碼，但它既不在 diff 宣稱的 before blob、也不在 after blob、也不在工作樹現檔裡，而且該 hunk 的行數頭本身就自相矛盾（無法用 `git apply` 套用）。這是全份 diff 裡**唯一**一處這樣的異常（其餘所有 hunk 逐行核對皆與真實 git diff 一致）。作為外部審查員，這代表**這份 diff 檔不能被當作對真實變更的忠實紀錄**——至少這一段是被插入/竄改進來、從未真的落地過的內容,必須在採信本次投稿前先查清楚來源(是產生 diff 的流程壞了,還是有人手動加料)。

**附帶（若這段程式碼真的存在，它本身也踩了本次審查鏡頭 1 的洞，供參）**：
```python
def _quote_coverage(report_path, spec_path):
    rows = _quote_rows(...)
    n_ok = sum(1 for r in rows if r["ok"])   # rows 可能是 None（_quote_rows 的合約：零引句回 None）
```
`_quote_rows` 的明文合約是「零引句回 None」（呼叫端 fail loud）；`cmd_quote_check` 與 `_loop_status_disposal` 兩處真實呼叫點都有判 `is None`，唯獨這個（不存在的）`_quote_coverage` 沒判，對零引句報告呼叫會是 `TypeError: 'NoneType' object is not iterable`。但因為這函式不在真實碼庫裡（見上），此點僅供對照，不單獨計入嚴重度。

---

## Finding 2（major）—— T6 留痕強制檢查：帳面任一行 JSON 壞掉就靜默失效（fail-open，非 fail-closed）

**file:line**：`scripts/lumos:2827-2834`（`cmd_canary` 內，T6 定錨檢查區塊；對應 diff 檔約 line 722-733）

**引句（逐字複製自 diff 檔）**：
「`if loop and path.exists() and not (report and snapshot):`」
「`except (OSError, ValueError):`」
「`_anchored = False   # 帳面壞行由既有讀側守衛處理,寫側不因此誤擋`」

**程式碼**（現況，與 diff 內容一致）：
```python
if loop and path.exists() and not (report and snapshot):
    try:
        import json as _json6
        _anchored = any(
            _json6.loads(_l).get("loop") == loop and "findings_set" in _json6.loads(_l)
            for _l in path.read_text(encoding="utf-8").splitlines() if _l.strip())
    except (OSError, ValueError):
        _anchored = False   # 帳面壞行由既有讀側守衛處理,寫側不因此誤擋
    if _anchored:
        print(f"ERROR: loop {loop!r} 已定錨為 disposal loop(帳面有 findings_set 記錄)——"
              "後續 record 必帶 --report 與 --snapshot(留痕強制;T6)", file=sys.stderr)
        return 2
```

**具體失敗場景**：
1. loop `L` 已定錨（帳上已有一筆帶 `findings_set` 的記錄）。
2. `.canary-log.jsonl`（同一顆帳、可能是別的 loop、甚至是別的無關記錄）**任何一行**因故壞掉——例如某次 append 中途被中斷、手動編輯留下半行——導致該行 `json.loads` 丟 `JSONDecodeError`（`ValueError` 子類）。
3. 這個 `any(...)` generator 是在 `for _l in path.read_text(...).splitlines()` 逐行掃**整個檔案**（不是只掃 loop `L` 的行）；只要其中任何一行解析失敗，例外就會冒出整個 generator，被外層 `except (OSError, ValueError): _anchored = False` 接住。
4. 於是即使 loop `L` **真的**已定錨，`_anchored` 被誤判為 `False`，`if _anchored:` 不觸發，`canary record --loop L`（沒帶 `--report`/`--snapshot`）就直接 rc0 通過——T6 宣稱的「定錨後每筆 record 必帶 report+snapshot(留痕強制)」被靜默繞過，且**沒有任何錯誤訊息**告知使用者發生了什麼。

**為什麼這是真隱患，不是可以忽略的邊角**：同一個檔案（scripts/lumos）在既有的 `cmd_loop_status` 讀取邏輯（line ~3572-3583，非本次 diff 新增）處理同一份 `.canary-log.jsonl` 時，做法是逐行 `try/except ValueError: n_badlines += 1; continue`——**壞行只跳過那一行，不影響其餘行的判讀**，並且明文注解「legacy/panel 維持容忍(行為不變)」。T6 這段新增程式碼沒有沿用這個既有慣例，而是整個 generator 一次性失敗、直接判定「未定錨」。這與 T4 `_loop_status_disposal`／整份設計反覆強調的「fail-closed」哲學（如 `# ── ① G3 hash 鏈(fail-closed:unbound 也擋——disposal 是新閘,無舊帳包袱) ──`）方向相反：一個不相干的壞行就能讓一個安全/留痕相關的閘從「擋」變成「放」，而且是悄悄地放。

**測試覆蓋缺口**：`t_disposal_loop_requires_provenance`（新增測試）只測了「已定錨 loop 缺留痕→rc2」與「未定錨 loop 不受影響」兩條路徑，沒有任何案例覆蓋「帳面含壞行時 T6 是否還擋得住」，所以這個回歸目前不會被現有測試組抓到。

**建議修法方向（僅供參考，非本次必須採納）**：把這段掃描改成跟既有 `n_badlines` 邏輯一樣的逐行 try/except、壞行跳過繼續掃，而不是整個 generator 包一層 try/except。

---

## Manifest 命中判定：governance/eval/canary_calibration.py:81

**引句（逐字複製自 diff 檔）**：
「`with log.open("a", encoding="utf-8") as f:`」

**判定：誤報（false positive），非真隱患。**

該行（連同下一行 `f.write(...)`）本來就包在 `with log.open("a", encoding="utf-8") as f:` context manager 裡，離開 `with` block 時 `f` 會被自動關閉，不需要也不應該再手動 `close()`。檔案內其餘的檔案存取（`rp.read_text(encoding="utf-8")`、`pathlib.Path(a.plants).read_text(...)`）用的是 `pathlib.Path.read_text()`，本身就是一次性讀取＋自行關閉，不持有懸掛 handle。全檔沒有任何裸的 `open()`/未關閉 handle。此檔案（含新增的 `governance/eval/canary_calibration.py`）在 diff 中是全新檔案（`new file mode 100755`），且與真實 repo 內容核對一致（不在 Finding 1 的異常範圍內）。

---

## 總結

- Finding 1（blocker）：`scripts/lumos` diff 中 `_quote_coverage` 一段 hunk 經 git blob 與行數頭雙重機械核對，證實是**全份 diff 唯一一處**與實際變更不符的內容——診斷結論是這份 diff 檔本身不可全信，需先查清楚來源再進入後續審查/合併流程。
- Finding 2（major）：T6 留痕強制檢查（`scripts/lumos:2827-2834`）在帳面任一行 JSON 壞掉時 fail-open，靜默繞過「定錨後必帶 report/snapshot」的留痕強制合約，且無測試覆蓋此路徑。
- Manifest 項（canary_calibration.py:81）：誤報，該檔案 handle 已用 `with` 正確管理。

**Max severity: blocker**（Finding 1，diff 完整性問題）。若排除 diff 完整性問題單看程式邏輯本身，max severity 為 **major**（Finding 2）。
