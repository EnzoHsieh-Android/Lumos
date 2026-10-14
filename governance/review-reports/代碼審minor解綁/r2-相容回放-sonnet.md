severity: major

我只核對了舊帳相容與回放這個鏡頭。派工詞尾端沒有附固定席節點,所以沒有逐條判的節點。

## 先確認設計說對的部分

- **既有凍結判定不變。** 我讀了 `governance/replay/` 底下 321 份 verdict.json,逐份看判定輪。判定輪有 major 席且 accepted 非空的,正好是 `code-審查跑滿回顧` r4 和 `code-待決問題改存開頭欄位` r9,兩份都是 rc1。`code-純文件子集` 的判定輪 r3b、`code-規格閘半套` 的判定輪 r3,accepted 都是空的。這幾句與帳面一致。
- **沒有任何凍結列帶 `finding_sources`。** 帳本是 append-only,沒有這個欄位,所以全部走舊分支,判定不變。
- **`_REPLAY_ENGINE_REV` 上線不動不會影響既有判定。** 這是按「既有凍結判定不變」推出來的結論。
- **讀 `finding_severities` 的地方沒有漏。** `scripts/lumos` 只有三處:寫側(約 10865 行)、逃逸自動記(約 11130 行)、`_fix_item_repeat`(約 14116 行)。`gov` 的 canary mapper 沒有投影這個欄位,所以不受影響。

## findings

severity: major
blocking: 是
引句:「路徑在 repo 裡存在且行號不超出檔長(沿用 refcheck 的解析)」
- 哪一句:S7 和辯方降級那步,放行理由裡的 file:line 要對現在的工作樹驗存在與行數。
- 照字面會發生什麼:`cmd_loop_replay` 的凍結閉包只收判定輪的 report 和 snapshot,以及資安席的檔,不收被引的原始碼檔。
  - 某輪靠 evidence 降級放行,當時過閘並凍結。
  - 之後被引的檔改名、刪掉或縮短。
  - 回放對閉包重算,新步驟讀到現在的樹,判成不過。
  - 這會被報成「邏輯漂移」(紅,rc1),但制度沒變。
  - `engine_rev` 沒變,所以不會被當成「golden 過期」而跳過。
- `_refcheck_scan` 讀的是活的 repo。
- 設計的回放段沒提這個非封閉輸入。S11 只測既有帳(沒有 `finding_sources`),抓不到。
- 應該是:file:line 對凍結快照或 `路徑@<提交>:行號` 的釘版本驗,或把被引的檔 blob 納入閉包。否則要明講這一步不進回放,並在回放時略過。
- 另外 refcheck 有「top_dirs 靜默過濾會把假目錄放行」的前科(`scripts/lumos` 約 28550 行的註解)。沿用時要確認不存在的頂層目錄會判不過。

severity: major
blocking: 是
引句:「不開放不帶反證的 major 放行(原報 major 只能折,或經辯方 evidence 加可核對 file:line 降級後放行)」
- ⚠ 判不準。這條落在設計威脅面,不全屬我的相容鏡頭。
- 使用者裁定的是「major 照舊必折」。這句字面上讓原報 major 可以放行。
- 閘只驗三件事:`refute_verdicts[id]=="evidence"`、放行理由裡有一個存在的 file:line、其餘條件。
- 威脅模型是 AI 編排者為了過閘而誤標,所以一個真的 major 只要多帶一個 `--refute-verdict id=evidence`,理由裡貼任一存在的 `scripts/lumos:1`,就能放行。設計自己也承認「閘只驗 file:line 存在,不驗反證內容對不對」。
- 這跟 WHY 寫的「洞沒有重開」互相矛盾。
- 應該是:要嘛把這條路從這份計劃拿掉(原報 major 一律只折,辯方降級另案裁),要嘛向使用者明講這是超出原裁定的新放行路徑,並補機械下限(例如反證 file:line 必須落在 snapshot 的 diff 或被審範圍內)。

severity: minor
blocking: 否
引句:「重現不到清單(refuted-set)不提供豁免:寫側規定它的 id 不得在發現清單,所以被列進去的原報 major 一定沒有 id 指到,由第 2 點擋下」
- 帳上有 461 個有 major 的代碼審輪,其中 24 輪(約 5%)載體的 refuted_set 非空。
- 這些輪只要帶了 `finding_sources` 又要放行任何 minor,就永遠過不了。因為被判重現不到的 major 沒有 id 可指,又不能補 id。
- 退路是不帶 `finding_sources`、全折。
- 這是設計刻意的取捨(S6),所以只是誤擋面,不算錯。
- 手冊要寫明這個退路,否則編排者會卡死。

severity: minor
blocking: 否
引句:「bump 會讓全部凍結判定變成過期、跳過重算」
- `_REPLAY_ENGINE_REV` 旁的註解寫「d5 判定語意改版就 bump」。設計選擇上線不 bump,理由是舊輸入判定不變,這在邏輯上成立。
- 但這跟註解的慣例相反,而且上線後凍結的、靠新步驟過閘的 golden,在尚未合併的舊版 `scripts/lumos` 上回放會報漂移。
- 設計應該明寫「這是對慣例的有意例外」,並加一句回放要用已含新步驟的版本。
- 回退段「必須 bump」的結論是對的。

severity: minor
blocking: 否
引句:「逃逸自動記按逐條嚴重度判,被放行的原報 minor 不會進逃逸帳」
- 「其他讀者行為會變」這段有兩處描述不準。
- **逃逸帳:** 席報告那幾列(沒帶 `finding_severities`)在記帳當下已按輪級 `severity=major` 自動記過逃逸,不會因後來被降級放行而撤。所以「經辯方降級放行的原報 major 也不會進逃逸帳」不成立,RETIRE-IF 和 REVISIT 的理由要跟著改。
- **修正關卡:** `_fix_item_repeat` 帶逐條嚴重度時,折入的 minor 本來就不當 major,這不是新行為,也不是「放寬」。
- 應該是:這兩條改成「沒有變化」,或改寫成真正有變的讀者。真正有變的是 `_cap_hint` 的折入數,因為放行的 minor 不再計入 folded。

severity: minor
blocking: 否
引句:「`_gov_event_types_ok` 同步加「值必須是字串清單」」
- 這句原文含「」。上面這行是方便找位置的摘錄,不是錨定引句。可錨定的原文是:`finding_sources` 的型別加進 `_GOV_FIELD_TYPES`。
- 現有的值檢查只是 `isinstance(v, str)`,list 值要另寫分支。
- 讀側(新步驟)沒寫遇到 `finding_sources` 不是 dict 或值不是字串清單時的處理。
- 手改帳或壞值會讓處置閘 traceback。其他欄位的慣例是 `isinstance(..., dict)` 後才讀,壞值 fail-closed,不噴例外。
- 應該補一句 fail-closed(判不過或 rc 2,不 traceback)。

總結:最嚴重等級 major,blocking 2 條(其中 1 條 ⚠ 判不準),另有 4 條 minor 不阻擋。
