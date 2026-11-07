severity: major

我用 importlib 載入 `scripts/lumos`,在臨時目錄直接呼叫 `_kt_bj_read`、`_kt_bj_check`、`_codeloop_write_marker`、`_render_gov_situation`、`_kappa2` 重現。沒有跑完整的 Android 型錄與真實推送流程,所以 F1、F2 的下游行為(check 是否照常擋)是用函式輸出加讀碼推得的。實驗用的臨時目錄已刪。

**F1 標記檔比治理帳舊時,標記檔照樣優先,帳上已有的盲判被當成沒有,「check 會退治理帳讀」的提示不成立**
引句:「提醒:本機標記檔沒寫成({e.__class__.__name__}),治理帳那一筆已經在了,check 會退治理帳讀」
file: `scripts/lumos:72220`(`_kt_bj_read`,標記檔能解析且有 `cells` 就直接回傳,不跟治理帳對)
file: `scripts/lumos:72569`
- 重現:
  - 輸入:治理帳有 s1、s2 兩段的第一盲判事件,標記檔只含 s1。
  - 實際:`list(_kt_bj_read(d,"feat/x").keys())` 回 `['s1']`,s2 被忽略。
  - 預期:標記檔缺的格要從帳補上,至少不能讓標記檔蓋掉帳。
- 觸發情境:盲判分多份寫(超過 30 段),第 2 份寫帳成功、寫標記檔 OSError。
  - 提示說會退帳讀,但標記檔已存在,不會退。
  - 本機 `code-loop check` 對 s2 誤報「缺第一盲判」,CI 讀帳卻會放行。
  - 本機與 CI 判定不一致,這就是「衍生資料以誰為準」的問題。
- 連帶問題:標記檔與帳各自「每格取第一筆」,但兩邊看到的歷史不同。
  - 重跑同一格,標記檔會收下較晚的那筆,帳裡第一筆仍是舊的。
  - `gov --stats` 讀帳,`check` 讀標記檔,兩處對同一格的票會不一樣。
severity: major
blocking: 是

**F2 標記檔只驗最外層是 dict,內層形狀不對會炸掉,被外層吞成 fail-open 放行**
引句:「if isinstance(d, dict) and isinstance(d.get("cells"), dict):」
file: `scripts/lumos:72227`
file: `scripts/lumos:73072`(`表態核對例外` 整段 `except Exception`,走 `_gate_failopen` 放行)
- 重現:標記檔內容 `{"cells":{"s1":{"D-1":"x"}}}`,呼叫 `_kt_bj_check(...)`。
  - 實際:`AttributeError: 'str' object has no attribute 'get'`。
  - 預期:當標記檔壞掉,退治理帳重建;至少不能放行。
- 實際後果:這個例外在 `code-loop check` 裡被 `except Exception` 吞掉,走 `_gate_failopen`,整個表態閘放行,盲判核對連同表態核對一起被略過。
- 同類問題:`{"cells":{"s1":{"D-1":{"first":{}}}}}` 因為只驗 `isinstance(first, dict)`,空 dict 就算「有第一盲判」,而且票是 na。
  - 治理帳重建那條路要求 `applies` 是布林,標記檔沒有同樣的要求。
- 註解寫「壞掉的標記檔跟沒有一樣」,只涵蓋 JSON 解析失敗,沒涵蓋形狀壞掉。
- 標記檔由工具原子寫入,觸發機率低,但出事時是放行方向,所以列 major。
severity: major
blocking: 是

**F3 `/` 與 `__` 被壓成同一個檔名,不同分支共用同一份盲判標記檔,且讀的時候不核對 `branch` 欄**
引句:「return Path(repo_root) / "governance" / "code-loop" / f"{_codeloop_branch_filename(branch)}.blind-judge.json"」
file: `scripts/lumos:69895`(`_codeloop_branch_filename` 把 `/` 換成 `__`)
file: `scripts/lumos:72198`
- 重現:`_kt_bj_marker_path(d,"a/b") == _kt_bj_marker_path(d,"a__b")` 為 True。
  - 我用 `feat/x` 寫了標記檔,再讀 `feat__x`:讀到的是前者的 `cells`,沒有退治理帳按分支過濾。
- 另一個撞法:分支 `x` 的標記檔 `x.blind-judge.json`,會撞上分支名叫 `x.blind-judge` 的留痕檔 `<安全名>.json`。
- 後果:
  - 一個分支的盲判被另一個分支讀到。
  - 另一個分支治理帳裡明明有的紀錄,被標記檔蓋住(同 F1)。
- `_kt_bj_read` 讀標記檔時應核對 `d["branch"] == branch`,不符就當沒有。
- 這個壓縮規則是既有慣例,表態標記檔也有同樣問題,但盲判是新寫入路徑。
severity: minor
blocking: 否

**F4 仲裁同第一盲判時,一律印「三方多數判作者沒照做」,沒檢查作者是不是答了不適用**
引句:「text": (f"段 {sg['seg']}({where})的 {rid} 三方多數判作者沒照做:作者 {_kt_bj_vote_text(av)};」
file: `scripts/lumos:72295`(`if _kt_bj_blind_vote(arb) == av` 只看仲裁是否等於作者,其餘全進 majority)
- 重現:作者答 `applies:false`,第一盲判與仲裁都判「適用且照做」。
  - 實際:`_kt_bj_check` 回 `majority` 一筆,文字是「三方多數判作者沒照做:作者 不適用;第一盲判 適用且照做;仲裁 適用且照做」,後面還叫作者「照型錄那列改碼後重表態」。
  - 預期:兩位盲判都說有照做,這不是「沒照做」,不該產生「多數判作者沒照做」的提醒。
- 另一個例子:作者「適用且照做」、第一盲判「適用但沒照做」、仲裁「不適用」,三方三種答案,也被印成「三方多數」。
- 這筆被寫進帳,又會被 `gov --stats` 的升擋統計數進去(仲裁照做算誤報),誤導 REVISIT:2027-01-08 的升擋決定。
- 提醒不擋,所以不是 major。
severity: minor
blocking: 否

**F5 錯誤的第一盲判寫進帳後沒有撤銷路徑,重跑只會被「以第一筆為準」略過,而且回傳碼是 0**
引句:「已有記錄,以第一筆為準:{len(skipped)} 格沒覆蓋(例:段 {skipped[0][0]} 的 {skipped[0][1]});同一段只認第一筆盲判」
file: `scripts/lumos:72559` 附近(`_cmd_codeloop_blind_judge` 的 skipped 輸出)
- 重現:代理對某格交了錯的第一盲判並寫入。
  - 再用正確的結果重跑,validate 照樣通過,又往 append-only 的帳多寫一筆重複事件,輸出 `✅ ... 記下來了`,rc 0。
  - 檢查和統計都只看最早一筆,正確票永遠不算。
- 目前唯一的繞法是改程式讓段身分換掉(統計裡也寫了「改無關空白換身分重抽也算在這」)。
- 這既汙染統計,也讓人以為重判成功。
- 至少要在整份都沒有新格寫進去時給非 0 的 rc 或明確說「這份完全沒生效」。
- 全部格都已存在時,也不該再往治理帳追加事件。
severity: minor
blocking: 否

**不適用的鏡頭**
- 後端卡 `be-authz` 對不上這次改動:這是本機 CLI 與本機帳,沒有多人資料的端點。
- 後端卡 `be-api-compat` 對不上這次改動:治理帳新增的 `blind_judge`、`role` 欄,舊讀者會忽略,舊帳讀進來走 `or "evidence"` 預設,我沒找到相容性問題。
- 盲性(鏡頭 2):`--template` 材料只含程式、型錄列與出處,沒有作者表態或他人票。
- 構造 JSON 的重複段、大小寫不同的段身分、多餘欄位,`_kt_bj_validate` 都會整份拒收,沒有誤放行路徑。
- 路徑穿越:分支名只把 `/` 換成 `__`,不會逃出目錄。
- `reason` 內的 U+2028 不會讓治理帳切行出錯(`_ledger_lines` 只認 `\r\n`、`\n`、`\r`)。
- kappa 邊界:樣本 0 回 None、單一答案回 None、全一致且兩類都有時回 1.0。`pe>=1` 有保護,沒有除以零的路徑。

總結:最嚴重是標記檔與治理帳不一致、標記檔形狀壞掉會走 fail-open(F1、F2),會擋 2 條。
