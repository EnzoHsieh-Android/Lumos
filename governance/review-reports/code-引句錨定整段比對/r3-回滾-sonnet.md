severity: minor

第 3 輪回滾與資料狀態鏡頭,我沒找到 blocking 問題。實驗在 `d6817180` 的 `--shared` clone 和改前 `cb832b56` 的 `scripts/lumos` 上做,結束後已刪掉我的實驗目錄。

**凍結、補凍、重算判定的入口**

- **`loop replay --freeze`**(`scripts/lumos:1126` 與 `:1140` 兩趟):只擋 rc2,rc1 照樣凍進 `verdict.json`。
- **`--freeze --note` 重凍**:同一條路徑,多歸檔舊檔和留治理帳。
- **週跑補凍**(`governance/autonomous_loop/replay_weekly.py`):同樣呼叫 `--freeze`,不先確認是綠。
- **`loop replay --golden`**(`:1268`):判準丟例外、章值不認得都算判失敗,與凍結時的「過」不同就報邏輯漂移。
- **即時處置閘**(`:13012`)和 **`loop next` 代問**(`:15691`):只用 rc,不解析輸出。

計劃〈實務隱患〉的清單和這幾個入口對得上。「凍結接受非綠」是既有設計,改前改後行為一樣,已另立 Issue。實際數字也對:帳上 307 份判定檔,5 份 rc1,fails 只有「留痕」或「處置集合」,沒有 `quote`。

**舊帳在新程式下是否一致(改前 `cb832b56` 對照)**

- **`_quote_rows_legacy` 本體**:函式本體與改前的 `_quote_rows` 逐行相同。
- **307 份 golden 回放**:新舊 rc 全相同(306 個 0、1 個 1),輸出只多一行 `[disposal] 引句判準:legacy(帳上無章)`。唯一的 rc1 是「消費專案接入靜默失效」的 intake sha 不符,新舊相同,計劃已記為 Issue。
- **372 個有 `spec_path` 的 loop 即時跑處置閘**:新舊 rc 與輸出完全一致(206 個 0、153 個 1、13 個 2),扣掉新增的判準行和 3 行診斷行。
- **診斷指令**:3 行裡我照抄跑了 2 條,結果與閘判的一致(一條報 2/5 句錨不到,一條零引句 rc2)。

**還原這個提交後帳上的欄位與事件**

- **第一階段的實際帳列**:寫側常數是 `legacy`,載體列只會多 `"quote_rule": "legacy"`。我用新程式記帳並凍結後,改前程式照樣回放「一致」,處置閘、`doctor`、`loop list`、`severity-check`、`verify-progress`、`canary-stats` 的輸出新舊相同。
- **第二階段才有的擋下事件**:我在 clone 裡臨時把寫側常數換成 `full-span-v1` 模擬。
- **`gov --stats` 的分格**:改前程式把 `quote-rule:` 事件算進「缺 refuted-set」,總數不變只是分格錯。計劃〈實務隱患〉最後一條已寫明。
- **`quote_rule` 欄**:改前程式不認得它,逐欄 `.get` 不受影響。

**處置閘新行會不會影響解析輸出的腳本**

- **新增的輸出行**:`[disposal] 引句判準:…`、`    診斷:…`,手動 `quote-check` 第一行 `引句判準:…`。
- **機械消費者**:`autonomous-loop.sh` 只看處置閘 rc,`replay_weekly.py` 只比對 `邏輯漂移`、`帳被動`、`凍結檔被動`、`佚失`、`golden 過期` 這幾個字樣,沒有人逐行解析 `[disposal]`。新行沒有這些字樣,結論是不受影響。
- **測試端**:`scripts/test_lumos.py` 以前綴 `[disposal] 資安席` 與 `[disposal] 跑滿回顧` 取行,新行不衝突。

**Finding**

1. 診斷指令的相對路徑與執行目錄綁在一起
severity: minor
blocking: 否
引句:「印給人照抄的指令:路徑用同檔的 _sh_quote 加引號(代碼審 r1 回滾席、r2 架構對齊席),開頭是 - 的補成 ./ 免得被當選項(r2 邊界席)」
file: `scripts/lumos:26507`
- 處置閘用 `--repo` 解析帳上的相對路徑(`_prov_path(rp)` 以 repo 根為底),診斷指令印的卻是帳上原樣的相對路徑,也沒帶 `--repo`。
- 從 repo 根以外的目錄跑閘時,照抄會得到「檔案讀不到」rc2,而不是閘判失敗的原因。
- 在 repo 根跑時沒問題(我照抄的兩條都能重現),所以只是不便,不影響判定。
- ⚠ 我沒有專門在 repo 根以外的目錄實跑這個情境,是從程式讀出來的。

總結:最高等級 minor,blocking 共 0 條
