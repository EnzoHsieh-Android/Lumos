severity: minor

我沒有建 worktree,所以沒有修前版本可對照。派工詞指定的鎖檔不存在,不需處理。

## 發現

### 1. 重估用「第一支」的實測當平均,冷編譯的第一支會讓合併整個平台組被停用
severity: minor
blocking: 否
引句:「if measured and mg.remaining() < sum(measured) / len(measured) * left * _CHOICE_MERGE_BUDGET_K:」
file: `/Users/enzo/harness/lumos-choice-speed/scripts/lumos:28984`
失敗場景:計劃〈做法〉2 說第一支單支基準會把整棵樹編譯過,所以第一支必然最貴。重估樣本只有第一支時,「平均」就等於這個冷編譯耗時。
- 實測輸入:3 支測試,總時限 24 秒,第一支 alphaCase 睡 8 秒、其餘約 0 秒。
- 走到的行:量完第一支,剩 16 秒;重估 8 × 2 × 1.5 = 24,大於 16。
- 結果:`_kill_merge_singles` 回 False,這個平台組記成 `(False, '基準')`,合併停用。實際剩下兩支基準加合併基準只需幾秒,預算其實夠。
- 影響:合併快篩被關掉、整次退回逐支跑。這是速度損失,不是資料錯誤,也不是資源超限。真實專案的冷編譯加第一支遠大於 5–6 秒時,這個情形會出現。
重現(臨時腳本,跑完已刪除):
```
python3.14 -I r.py
# 輸出 plats {'kotlin-junit': (False, '基準')} survived {}
```
腳本用 `m._KillMerge(monotonic()+24, 2)` 和 `_ckm_repo(2, {"__base_sleep_by__": {"alphaCase": 8}})` 設定,在修後 HEAD 的 repo 路徑上跑。
歸因:未判定。我沒有跑修前版本;依修補說明,修前沒有重估(未驗證),所以修前不會有這個停用。算有證據的修補新增行為,但代價是速度,不是回歸錯誤。

## 已驗主張(資源鏡頭)

引句:「if merge is not None and merge.interrupted:   # 訊號在登記之前就來過:回呼沒看到這支,當場收掉」
- 登記之後才檢查旗標,所以訊號在檢查前或檢查後到,都會有一個人收掉合併程序。
  - 檢查前到:這行收掉。
  - 檢查後到:`on_signal` 已能在登記表裡找到它並收掉。
- `_kill_proc_group` 自己吞掉所有例外,不會留下例外而漏掉後面的 `communicate`。
- `finally` 照舊會把程序從 `_KILL_RUN_LIVE` 拿掉。這一段通過。

引句:「return min(max(m_el * 5, floor), max(remaining, 1.0))」
- 快篩逾時上限現在受剩餘總時限約束。
- 剩餘時限用完時,`_kill_merge_screen` 在開快篩前先看 `should_stop`,不會開跑。
- 剩餘時限很小但大於零時,上限只有 1 秒或剩餘值,快篩逾時,結果被丟、走逐支,最多連 5 次後斷路器停用。這是預期行為。

引句:「if b_to and cap < full:   # 被剩下時限截斷:不算這支的基準」
- 被截斷的那支不寫進基準,回 False 走逐支,逐支照完整上限重量。
- 已量完的基準保留,沒有資料遺失。

測試新增項的暫存:
- 中斷測試新加 `keep_worktree=True`,收尾刪的是 `_isolated_worktree` 用 `mkdtemp` 自己建的 parent 資料夾,範圍是自己的。
- `big` 模式改成每支都寫進結果檔,只受大小檢查影響,寫在測試自己的暫存樹,收尾由 `_ck_cleanup` 刪。

## 未驗範圍
- 沒跑 `python3.14 scripts/test_lumos.py -k` 的任何測試。
- 沒有修前版本的行為證據。
- 沒驗在真 Gradle 下合併程序在 `proc.wait()` 之後的孫程序殘留。

## 三問答覆
- ①原問題(時限吃光、快篩逾時不受限、訊號空窗)的修復效果:程式碼層面上述三處成立。行為證據只有我對重估的一次實測,別處靠讀碼。
- ②修補處的正常、錯誤與相鄰路徑:正常路徑、截斷逾時路徑、中斷路徑都走過一遍,仍成立。
- ③新發現的修前修後對照:發現 1 沒跑修前版本,未判定。

總結:最高嚴重度 minor
