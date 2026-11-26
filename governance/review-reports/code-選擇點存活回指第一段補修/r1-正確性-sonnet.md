severity: major

鎖檔 `774286c7…json.warming` 已經不存在,我沒有刪任何鎖,照派工詞審查。

**Finding 1:新舊互讀(舊快取沒有 .base.json)的退路沒有任何測試守**

severity: major
blocking: 是

`scripts/lumos:29264`:`cached()` 靠 `base is not None` 判斷舊快取。舊快取只有 `.exec`、沒有 `.base.json`,要走刪檔重量那條路。

引句:「if data is not None and base is not None and _choice_cov_exec_classes(data) is not None and not self.robo_zero(data):」

失敗場景:
- 把 `base is not None` 拿掉,`_choice_cov_base_read` 回 None 時 `setdefault(…, None)` 會把 None 寫進 `c.baselines`。
- 之後合併快篩讀 `c.baselines[...][4]` 會 TypeError。
- 這個壞法沒有測試會紅。

最小重現,我在臨時 clone 上做過:
1. 把該行改成 `if data is not None and _choice_cov_exec_classes(data) is not None and not self.robo_zero(data):`。
2. 跑 `python3.14 scripts/test_lumos.py -k choice_cov_resume`,結果 5 passed, 0 failed,沒有紅。

原因:`t_choice_cov_resume` 的第二次跑讀的是本版寫出、帶 `.base.json` 的快取,從來沒有「有 `.exec`、沒有 `.base.json`」的案例。

同樣沒有案例的還有:基準檔 `rc != 0`、型別不對、超過 64KB、JSON 損壞,這些 `_choice_cov_base_read` 的拒收分支都沒測。

補法:加一案,只放 `.exec`、不放 `.base.json`,斷言它被重量,且 `baselines` 沒有 None。

**Finding 2:圖譜裡有一行現況描述跟新程式相反,diff 沒改到**

severity: minor
blocking: 否

`docs/lumos-toolchain-knowledge/Systems/規格閘.md` 的 WHY「覆蓋可信看專案類別有紀錄數」在 diff 裡是未改動的內文,仍寫:
- 套件是「改到的原始檔 package 宣告」。
- Robolectric 看「有沒有 org/robolectric/ 開頭的類別」。

這兩句正好是這次補修推翻的舊行為。

引句:「數類別名所在套件是改到的原始檔 package 宣告(沒有宣告是預設套件)而且有探針為真的類別;是不是 Robolectric 測試看那支的覆蓋資料有沒有 org/robolectric/ 開頭的類別」

同一檔新增的兩條 PITFALL 已經寫了新行為,所以這篇內部自己矛盾。下一個讀者會先讀到舊的那句。這句只是線索、不能推翻程式碼,但應該就地改寫。

**Finding 3:Robolectric 判定訊號與失敗模式可能同源**

severity: minor
blocking: 否
未能重現,所以自降一級。

`scripts/lumos:29605`(新 `_choice_cov_exec_robo`):

引句:「return any(hit and name.split("$", 1)[0] in _CHOICE_COV_ROBO_ENV for name, hit in cl)」

推測的場景:
- 原本判 Robolectric 看的是 runner 類別。那些類別在 app classloader 載入,有 CodeSource,不管 `includeNoLocationClasses` 有沒有生效都會被記到。
- 現在改看 `AndroidTestEnvironment`、`AndroidSandbox`。我推測它們由 Robolectric 自己的 sandbox classloader 定義、沒有 CodeSource。如果 `includeNoLocationClasses` 沒生效,它們可能也不被記。
- 若如此,設定壞掉時 `robo` 判成 False,Robolectric 測試的 0 被當成「真的沒碰」。
- 專案同時有會記到專案類別的一般 JUnit 測試時,`any_proj` 為真,新加的「全部都 0」斷路也擋不到。
- 結果是整行被判 `none`、不跑就記存活。方向是多擋,而且有 `cov-audit` 抽查兜底。

計劃只寫了「正確設定下 334 份有 runner、284 份有環境類別」,沒有「設定壞掉時環境類別還記不記得到」的資料。建議補一次關掉該設定的實測,再決定這個訊號可不可靠。

**其餘各 hunk 逐一走過,沒有找到會做錯的輸入**
- `_choice_merge_facts` 與 `_choice_merge_ghost_suite`:`tq.junit` 先擋 DTD 與過深,`zero_cases` 在 `suite_error` 之前判,空殼略過的邏輯成立。
- `red_rerun` 的斷路移到重跑之後:不掛也逾時的慢測試不會再誤斷路。
- `store` 先寫 exec、再寫 base:中途失敗只會變成快取沒命中,不會壞資料。
- `settle` 的全零斷路:`got` 為空時不觸發。

**圖譜固定席(Systems/guard-kill、規格閘等 37 篇)**
- guard-kill.md 的 PITFALL 與 `_kill_signal_marked` 那行跟程式一致。
- 規格閘.md 見 Finding 2。
- 其餘固定席節點沒有被這次改動推翻的內容。

臨時目錄 `/tmp/lumos-seat-work/code-選擇點存活回指第一段補修/r1-正確性-sonnet` 已用字面絕對路徑刪除。

總結:最高等級是 major(1 條,Finding 1:舊快取沒有 `.base.json` 的退路無測試)
