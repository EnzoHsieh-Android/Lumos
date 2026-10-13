severity: minor

這次改動沒有 blocker 或 major。我查出兩條 minor,都有當場能重現的證據,三問見最後。以下所有重現都在 /tmp 複本上跑,沒有呼叫 `claude -p` 或 `codex`,複本已刪。

**1. plugins 清單裡的非 dict 元素被靜默丟掉,bad_fields 不記,指紋跟「沒有外掛」相同**
severity: minor
blocking: 否
引句:「plugins = sorted(f"{p.get('name')}@{p.get('version')}" for p in _env_list(init, "plugins", bad) if isinstance(p, dict))」
file: `scripts/scenario_probe.py:394`(`_env_fingerprint` 內)
1. 輸入:init 的 `plugins` 是清單,但元素不是 dict(例如 `["a@1","b@2"]`、`[["a","1"]]`、`[None,3]`)。
2. 走到 `_env_list` 時它是清單,所以不記 bad。接著 `isinstance(p, dict)` 把元素全部濾掉。
3. 壞在:指紋跟 `plugins=[]` 一模一樣,`env.bad_fields` 也沒有 plugins。我在複本上驗了三種輸入,`env_fp` 都等於 `plugins=[]` 的指紋,`bad_fields` 都是 None。
4. 這跟 r2 修補要補的「型別不對要記下、不能靜默」是同一類問題,只是補在清單層、沒補到元素層。
5. 同一類的還有兩處:`_env_names` 對 dict 元素缺 `name` 時一律取 `""`。`mcp_servers=[{"id":"a"}]` 與 `[{"id":"b"}]` 指紋相同,`skills=[{"name":"s1"}]` 與 `["s1"]` 指紋也相同。
6. 現行 Claude Code 格式不會這樣,所以影響只在格式改版時,屆時換外掛看不出指紋差異。這個場景是假設的,所以只列 minor。
7. 歸因:有證據的原有漏查。查證:`grep -n "isinstance(p, dict)" /tmp/code-probefp-r3-repair.patch` 顯示修前就有這個 `isinstance` 篩選,修補只改了 `_env_list` 的簽名。

**2. 有三層保護沒有只靠它才會過的斷言,拿掉照樣全綠**
severity: minor
blocking: 否
引句:「variants = {」
file: `scripts/test_lumos.py`(`t_probe_env_fingerprint_stable_fields`,diff 檔 test 段)
1. 方法:在 /tmp 複本上對 `scenario_probe.py` 逐個破壞,跑 `t_probe_env_fingerprint_*`、`t_probe_history_records_env_fps`、`t_probe_run_one_records_env_fp` 與 `t_probe_summary*`。
2. 能翻紅的有這些:
   - 拿掉外層 `try`(M1)
   - 解析只接 `ValueError`(M2)
   - 型別不對不記 bad(M3)
   - 型別不對改成丟例外(M4)
   - `tools` 進指紋(M5)
   - null 算一種環境(M6)
   - 掛鉤不限 init 之前(M7)
   - `env_missing` 原因拿掉(M10)
   - 統計用 results 而不是 valid(M11)
   - Codex 結果不記指紋(M12)
3. 拿掉後全綠、沒人守的有三個:
   - 拿掉 `plugins` 的 `sorted(`(M9,改成 `list(`)。拿掉 `skills`、`mcp_servers`、`agents`、`slash_commands` 共用的 `_env_names` 裡的 `sorted(`(M15,改成 `list(`)也一樣全綠。測試裡每個清單最多兩個元素,而且只用「加元素」的變體,沒有任何「同集合、不同順序,指紋要相同」的斷言。排序是「只受穩定欄位影響」的核心,Claude Code 若以不固定的順序列外掛或 skill,指紋就會每場不同,測試抓不到。
   - 把 `_env_names` 改成不取 `name`,改用整個 dict 的字串(M17)。測試沒有「同一個 MCP 伺服器的 `status` 從 connected 變 failed,指紋不變」這條,所以 status 或 source 滲進指紋也抓不到。
   - 拿掉 `run_one` 與 `run_one_codex` 提早返回點的 `env_fp: None`(M13、M14)。實際影響低:這兩條路徑的結果理由以「儀器例外」開頭,本來就被排除在 `valid` 之外。
4. 此外 `[:12]` 的長度也沒有斷言,不列為問題。
5. 歸因:有證據的原有漏查。這些保護都是修補後才有,但修補宣稱「每一層保護各有只靠它才會過的斷言」,排序層與狀態欄位排除層不在其中。

**其他觀察(未列為 finding)**
- 輸出一行裡若含原始的 U+2028,`out.splitlines()` 會把那行切碎,init 就解析不到。`env_missing` 會寫成「輸出裡沒有 system/init 事件」,原因說錯,但真正的 init 事件還在。這個切行是本來就有的行為,`tool_calls_from_stream` 也吃同一份切法。我造的輸入是 `skills=["a\u2028b"]`,是否真有 Claude Code 版本會送這種字串我沒證據。
- 單獨的代理字元(如 `"\ud800"`)會讓整個指紋退成 null,`env_missing` 寫「取指紋失敗:UnicodeEncodeError」。這跟「欄位當空」可以分辨,行為符合設計。
- `env_mixed` 的判定:只有不同的非 null 指紋超過一種才標。我看過 null 加一種、Codex 全 null、有效場次為空這幾種,行為都符合「真的有兩種環境」。
- 相鄰路徑:`main` 呼叫 `summarize_results`、`history_record` 的地方,以及 `test_autonomous_loop.py:1924` 與 `:1946` 的 `run_one`,都沒有需要修改的地方。`governance/autonomous-loop.sh` 只用 grep 解析「個情境 Claude 自己敲對了」那行,不受 `env_fps` 影響。消融腳本那邊我沒找到 `summarize_results` 或 `history_record` 的呼叫。
- 無關的 `hashlib` 匯入搬到頂層沒問題,`main` 內用到雜湊的地方仍可用。
- `be-api-compat`:新增的結果鍵與 `env_fps` 都是只增不改,讀舊紀錄的人不受影響。`be-authz` 不適用,這支檔沒有端點。

**三問**
1. 原問題的修復效果:型別不對時,`plugins`、`skills`、`mcp_servers`、`slash_commands` 的指紋等於當空的,且 `bad_fields` 有記,測試確認過。`tools` 進指紋會翻紅,工具清單不再影響指紋。取不到加一種真指紋不標混用。深層巢狀 JSON 與編碼不了的字元不丟例外,拿掉保護各自會翻紅。
2. 相鄰路徑:正常、逾時、Codex、前置驗證失敗四條路徑都仍帶 `env_fp` 欄位。`valid` 只算有效場次,舊呼叫者沒有 `env_fp` 時 `env_fps` 為 None,歷史列不寫該欄。
3. 新發現的案例:finding 1 在修前與修後行為相同,指紋都等於 `plugins=[]` 且沒記 bad,不是修補造成的回歸。finding 2 的幾個破壞點是新測試才有的保護層,修前沒有這些層,所以無從比較。

總結:最高等級 minor
