# r2 對抗審計報告(code-dloop-redesign r2-s3)

審查對象:`/private/tmp/.../scratchpad/codeloop/code-dloop-redesign-r2-s3.patch`(r1 findings 修復批,vs repo HEAD `ba3ae1f`)。
方法:逐 hunk 讀完整份 diff → 對每個修復以 `scripts/lumos` 真代碼跑機械 repro 驗證(非只讀 code 猜)。

---

## Finding 1 [blocker] 診斷:diff 檔內「`_jsonl_append_verified` 重試」整個 hunk 不存在於真代碼——review 的是一份未落地的修復

**file:line**:diff 檔第 91–103 行(`scripts/lumos` 舊行號 `@@ -2853,6 +2871,10 @@`,對應真檔 `_jsonl_append_verified`,`scripts/lumos:2865-2876`)

**引句**:「try:   # dsp_retry_once: 暫時性 IO(NFS/防毒鎖檔)常見,重試一次再放棄」

**證據**:
- `git diff HEAD -- scripts/lumos governance/eval/canary_calibration.py scripts/test_lumos.py skills/lumos-design-loop/SKILL.md` 與給定 patch 檔逐位元組比對(同用 `-U10` 消除 context 行數差異),**唯一差異**就是這個 hunk——其餘全部 552/565 行完全吻合。
- 真檔 `scripts/lumos:2865-2894`(`_jsonl_append_verified`)現狀仍是 r1 之前的單次寫入版本:`except OSError as e: print(...); return 2`,**沒有第二個 `open(path,"a")` 重試區塊**。
- `grep -rn "dsp_retry_once" /Users/enzo/harness/lumos-toolchain/` 全庫零命中。
- 字串 `"ERROR: 寫入 {path} 失敗"` 在真檔內只出現 **1 次**(line 2875);若重試 hunk 真的落地,理應出現 2 次(一次原 except、一次巢狀 except)。

**失敗場景**:此 patch 的 7 個宣稱主題(canary-log 壞行/round-id/留痕重驗/相對路徑/非UTF-8/quote-check/校準讀回)裡**不含**這條重試修復,它明顯是誤混進這份 diff 的額外 hunk(或本該是另一輪未落地的草案)。任何依這份 diff 判定「r1 的『瞬時 IO 失敗直接 rc2』顧慮已修」的人都會被誤導——真代碼裡這個顧慮**仍未修**,而 diff 卻讓人以為已修。這是本輪最該抓的洞:diff 本身不可信,逐 hunk 核對真代碼才抓到。

**附帶**:即使這段重試邏輯將來真的落地,寫法本身也有冪等疑慮——`open(path,"a").write()` 在 TextIOWrapper 緩衝下,OSError 可能發生在 `close()` 的 flush 階段(此時部分位元組可能已落盤),此時盲目重試會在半行殘骸後面再疊一行完整記錄,造成 `.canary-log.jsonl` 出現「半壞行+重複行」——恰好是這批 patch 自己在①③修的「壞行/竄改」問題的製造者。若要落地,建議重試前先 fsync/驗證檔案大小未變,而非無條件二次 append。

---

## Finding 2 [blocker] `_loop_status_disposal` round-id 分組把「__legacy」寫死成單一 key,合併了本應各自獨立的 round-less 判定輪——直接打破既有相容測試 `t_disposal_loop_requires_provenance` 示範過的場景

**file:line**:diff 檔第 183–191 行(對應真檔 `scripts/lumos:8140-8151`,尤其 `line 8144`)

**引句**:`rid_ = r.get("round") or "__legacy"`

**證據(機械 repro,對真檔跑)**:
```python
# 兩筆彼此獨立、各自合法、都不帶 --round 的 disposal 記錄(T6 錨定測試本身就示範這種寫法:
# t_disposal_loop_requires_provenance 首筆就是不帶 --round 的 findings-set 記錄)
canary record caught --loop X --findings-set F1 --folded-set F1 --report r1 --snapshot s1 \
    --spec spec@v1 --reviewed h1   # rc0
# spec 改版後,第二輪獨立判定
canary record caught --loop X --findings-set F2 --folded-set F2 --report r2 --snapshot s2 \
    --spec spec@v2 --reviewed h2   # rc0
loop status X --disposal --spec spec@v2 --repo <root>
```
實際輸出:
```
[disposal] G3 hash: ✗ — 同輪 hash 分裂——各席 reviewed 或 result 不一致(同輪宣稱多個版本)
ERROR: 判定輪 __legacy 有 2 筆帶處置帳(每輪至多一筆;同 clusters 慣例)
rc=2
```
兩筆各自都合法留痕、各自都能單獨通過 disposal(逐一測試皆 rc0),但因為新分組邏輯把**所有不帶 `--round` 的記錄一律塞進同一個 `"__legacy"` key**,第二筆一寫入,舊分組就把兩筆合併當成「同一個判定輪」,觸發「同輪 hash 分裂」與「一輪多筆處置帳」雙重誤判。

**修復前(舊碼)行為對照**:舊碼 `r.get("round") or f"__seq{len(groups)}"` 讓每筆 round-less 記錄各自獨立成組(`__seq0`, `__seq1`, ...),`latest` 永遠只取最後一筆——不會有這個合併問題。這是 r2 這次改動(為了移植 round-id 非連續重現檢查)親手引入的回歸。

**失敗場景**:任何走 legacy(不帶 `--round`)路徑、且會**累積多筆**留痕記錄的 disposal loop(T6 錨定測試明文示範這種寫法合法),一旦第二筆記錄寫入,`--disposal` 就永久 FAIL/rc2——即使兩筆各自留痕、sha、quote-check 全部通過。這直接違反 SKILL.md 與 T6 測試載明的「相容鐵則:未定錨/舊 loop 完全不受影響」。新增測試 `t_disposal_gate_r1_panel_hardening` 只覆蓋帶 `--round` 的情境,沒人測到這個角落。

---

## Finding 3 [major] `_loop_status_disposal` 的 `n_badlines` fail-closed 檢查沒有按 `loop_id` 收斂範圍——同一本共用 `.canary-log.jsonl` 裡任何一筆不相干 loop 的壞行,會癱瘓所有其他 loop 的 disposal 閘

**file:line**:diff 檔第 178–181 行(對應真檔 `scripts/lumos:8138-8141`;`n_badlines` 計數源頭在 `scripts/lumos:3590-3606`,未隨此改動收斂到單一 loop)

**引句**:「ERROR: canary-log 含 {n_badlines} 行不可解析——disposal 閘 fail-closed」

**證據(機械 repro,對真檔跑)**:
```
loop Y 正常留痕一筆 → loop status Y --disposal ...   # rc1(輪無效,符合預期)
在共用 .canary-log.jsonl 尾端手動追加一行「不相干、無法解析」的壞行(不屬於 loop Y,甚至無法歸屬任何 loop)
loop status Y --disposal ...   # rc2
```
實際輸出從 rc1 → rc2,訊息:「ERROR: canary-log 含 1 行不可解析——disposal 閘 fail-closed(壞行使「判定輪=最後一輪」不可信;修帳或隔離壞行後再問)」——但那行壞行跟 loop Y 完全無關。

**根因**:`cmd_loop_status`(`scripts/lumos:3590-3606`)讀整本 `.canary-log.jsonl` 累計 `n_badlines`,**在按 `loop` 欄過濾之前**就計數壞行,之後把這個全域計數原樣傳進 `_loop_status_disposal`。`.canary-log.jsonl` 是整個 vault 共用的單一帳本(`path = env.vault.parent / ".canary-log.jsonl"`),被所有 design-loop session 共同追加。

**失敗場景**:給定情境屬於「自主迭代 loop 每天自動跑」的多 loop 並存環境(見專案記憶),只要**任一** loop 的留痕過程留下一行壞資料(哪怕是完全不相關、甚至無法辨識歸屬哪個 loop 的雜訊),**所有其他 loop 的 `--disposal` 都會被鎖死 rc2**,直到有人手動清帳——這已經超出①的修復意圖(「壞行使『判定輪=最後一輪』不可信」講的是同一 loop 內部次序被壞行干擾,不該波及不相干 loop)。新增測試 `t_disposal_gate_r1_panel_hardening` 的①案例只驗證同一 loop 自己的壞行,沒有測到跨 loop 誤傷。

---

## Finding 4 [major] `canary_calibration.py` 的「寫後讀回自驗」用「檔案最後一行」定位自己剛寫的紀錄,對併發寫入不安全——恰好在它宣稱要防的併發場景下會假失敗

**file:line**:diff 檔第 17–23 行(對應真檔 `governance/eval/canary_calibration.py:83-89`)

**引句**:`tail = log.read_text(encoding="utf-8").splitlines()[-1]`

**分析**:此修復的動機(見同段註解)是防「中斷/併發可留半行且無人發現」,並宣稱「沿 lumos `_jsonl_append_verified` 慣例」。但 `_jsonl_append_verified`(`scripts/lumos:2865-2893`)的自驗法是**掃全檔找唯一鍵(token)是否存在**,不管它落在哪一行、也不管別的 process 有沒有插隊寫入;這裡的實作卻假設「我剛寫的那行一定還是檔案最後一行」。`calibration-log.jsonl` 依 docstring 明文是「累積帳」,可被多次獨立呼叫(不同 `--config`,適合平行/排程跑批量校準)共用同一個檔案追加。

**失敗場景**:兩個 calibration 行程(例如不同 `--config` 平行跑,或使用者手動+排程重疊)各自成功把自己的 entry append 完畢後,若行程 A 的 `close()` 完成到它自己執行 `log.read_text()` 之間,行程 B 的寫入插進來完成,則行程 A 讀到的 `splitlines()[-1]` 是 B 的紀錄而非自己的——`json.loads(tail).get("ts") != entry["ts"]` 為真,行程 A 印出「ERROR: calibration-log 讀回自驗失敗」並以 rc2 收場,**即使它自己的資料已經正確落盤**。這正是 r1 該修的「併發窗口」議題本身,只是這次修復用了一個對併發不安全的驗證法,在併發下製造假陰性(誤報失敗),而不是它原本要抓的「半行/遺漏」真陽性。

---

## 結論

max severity: **blocker**
