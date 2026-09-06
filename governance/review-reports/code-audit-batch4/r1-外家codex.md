severity: major
- [major] 零斷言守衛把多個合法的平台／來源缺席分支判成失敗
  引句:「pass   # 消費端沒有這個範本;不印綠」
  位置:`scripts/test_lumos.py:4323`
  why: 此分支與 `t_export_quote_escape`、`t_init_existing_resyncs` 仍以 `pass; return` 跳過，既有 `t_precommit_vendored_exempt`、`t_precommit_shebang_script_counts_as_code` 也會在非 POSIX 平台直接 return；它們全部會被新 runner 判紅而非 skip。靜態掃描 624 支 `t_` 雖然每支至少含一個 `check`，但這些合法路徑能在第一個斷言前結束。應統一拋 `_SrcOnly`。十處新 raise 都發生在暫存目錄建立前，未發現跳過 finally 或清理的語意回歸。

- [major] 已被工具正式讀取的 `core_refs` 與 `regen` 遺漏於已知鍵清單
  引句:「"signed_off", "kill_recipes",」
  位置:`scripts/lumos:3255`
  why: 對所有 `fields.get()` 靜態對帳後，差集為 `core_refs`、`regen`；前者由跨圖譜影響分析讀取，後者由 regen lint／檢查讀取。合法節點會收到「工具不認得、任何檢查都不讀」的錯誤敘述，且要求消費者用 extra 設定掩蓋工具自己的正式 schema。每次 lint 僅約欄位數×28 次短字串比較，效能不是問題；真正的噪音來源是這個漏列。

- [major] 單源守衛只認 Codex 0.100–0.199，版本演進後會漏抓並讓反面測試假紅
  引句:「ver = _re.compile(r"\b0\.1\d{2}\.\d+\b")」
  位置:`scripts/test_lumos.py:26383`
  why: `0.200.0`、`1.0.0` 或兩段式版本均不匹配；屆時把新版本事實重新抄回 SKILL.md 不會被抓，而要求 templates.md 必須匹配此正則的反面斷言又會直接失敗。它也會誤中同形狀但非 Codex 版本的数字，例如其他工具版本或位址片段，因測試只看同頁是否含泛用的「唯一來源」等字樣。

- [minor] 多個近名候選的提示結果依 set 迭代順序漂移
  引句:「_hint = f"——是不是想寫 {_near[0]}?" if _near else」
  位置:`scripts/lumos:3315`
  why: `_known` 是 set，像未知鍵 `reated` 同時距 `created`、`related` 都是 1，卻任取 `_near[0]`，不同執行環境可能給不同且誤導的唯一建議。空字串、單字元不會越界；大小寫差一字元會被當作一次替換，沒有崩潰問題。
