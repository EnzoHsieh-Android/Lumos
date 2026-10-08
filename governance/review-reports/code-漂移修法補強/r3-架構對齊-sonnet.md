severity: clean

# 第 3 輪 架構對齊-sonnet 報告

本輪沒有 finding。逐項對照既有做法,結果如下。

## 一、兩態判斷 vs 既有 `_vendored_skip` 及其他 `_vendored_state` 呼叫端
- 讀 git 版本的寫法沿用既有:`_vendored_state(root, "")` 讀暫存區,跟每支檔有家暫存模式同口徑。file: `scripts/lumos:24511`(`_vendored_state(root, "")[0]`)、`scripts/lumos:24643`。改前 `"HEAD"` 走同一函式的 ref 分支(`_lens_git show ref:path`),沒有另寫讀檔邏輯。file: `scripts/lumos:17820-17831`。
- 口徑不同處有寫理由:`_vendored_skip`(`scripts/lumos:17867-17875`)是 `end 原封不動 | (start 原封不動 - end 已不存在)`,問的是「改完之後要不要掃這支的內容」;新的 `_delguard_vendored_skips` 刪除行要求 `改前原封不動 且 (改後原封不動 或 已不在)`,問的是「被刪掉的行是不是工具自己的」。docstring 逐段寫了差異與原因(專案改過的工具檔被 lumos update 蓋回,刪的是專案自己的名稱)。新增行只看改後原封不動,跟 `_vendored_skip` 的 `_intact_end` 那一半同義(已不在的檔沒有 `+` 行,不需要另一半)。不算第二種做法。
- 沒有 HEAD 時改前當空集合:`_vendored_state` 對 `show` 讀不到本來就走「不在、非原封不動」,`_json_at_ref` 對應清單也讀不到 → 空集合,不是新分支。file: `scripts/lumos:17824-17832`。
- 工具鏈本體回空集合:沿用 `_is_toolchain_repo` 前置,跟 `scripts/lumos:24511`、`scripts/lumos:17870` 同一寫法。
- 提早離開(diff 裡沒有任何 `_VENDORED_ALL` 路徑就不算兩態):既有呼叫端沒有這個 diff_text 提早離開,但這是新函式自己的省呼叫優化,只會多算不會少算(改名時來源路徑會出現在 `rename from` 行),沒有跟既有做法衝突。
- 跨層:守衛層直呼 `_vendored_state`(內部再走 `_lens_git`/`_json_at_ref`),跟 `scripts/lumos:24511`(nodehome)、`scripts/lumos:18399` 等呼叫端同層級直呼,不是新的跨層。

## 二、c4 目錄名對應與格式字元跳脫
- NFC 只當比對鍵、印磁碟現存名:`nfc()` 是既有 helper(`scripts/lumos:388`),沒有另寫 `unicodedata.normalize`。`_drift_c4_existing` 從磁碟列目錄,跟 `scripts/lumos:1861-1869` 那段「git 路徑第三段 + `is_dir()` 排除散檔」同一形狀(路徑至少四段、非目錄項排除)。
- 顯示跳脫:`_drift_c4_show_name` 是疊在既有 `_nodehome_show`(`scripts/lumos:23663`,非 UTF-8 → 替代字元)之上、外面再包既有 `_esc_clean`(`scripts/lumos:9765`,控制字元換空格)。它只補 `_esc_clean` 不處理的 Unicode 類別 Cf,是延伸不是另起一套;既有專案內沒有 Cf 顯示跳脫可重用(grep `202e|bidi|Cf` 只有 `_strip_zero_width` 是拿掉、用途是搜尋詞正規化,不是顯示;`scripts/lumos:3657-3665`)。docstring 已寫「只在這一處,不改共用的 `_esc_clean`」的理由。函式內 `import unicodedata` 與 `scripts/lumos:28196` 的 `_drift_git_cmd` 同寫法(雖然模組頂部 `scripts/lumos:62` 已 import,但既有處也是區域 import,不算新做法)。
- 補充指令:`_drift_c4_more_cmd` 沿用 `_drift_git_cmd` 的 `--literal-pathspecs`/`core.quotePath=off` 寫法,sha 只有十六進位、其餘固定字面,沒有外來字串,沒有另寫 shell 轉義。

## 三、佔位字檢查位置
- 仍在 `_set_conditions_locked`(`lumos set` 整欄改 valid_under/revalidate_when 的單一入口),用 `_SET_COND_SLOTS` 與 `_SET_COND_SLOT_VARIANTS` 兩層(精確 + 變體);跟 `_DRIFT_PLACEHOLDER_RE`(擋 `drift fix --reason`,`scripts/lumos:27653`)用途不同,註解已寫「不合併」。本輪只是收窄變體 regex,位置與結構不變。

## 圖譜鏡頭逐條判定
- `Systems/存量漂移守衛.md`(家):本輪修法都落在它管的 drift/delguard 顯示與判斷,diff 已同步改該篇與 delguard.md,不影響其他宣稱。
- `Systems/bound-tests-gate.md` ★INVARIANT★:合約管「code-loop check 逐支跑綁定測試」,本輪不動閘的判定邏輯,不影響。
- `Systems/guard-kill.md` ★INVARIANT★:guard kill rc 優先序與 --json 純度,本輪沒動 guard kill 路徑(只有共用 `_guard_settle_missing_say` 是前輪的事),不影響。
- `Systems/授權與歸屬.md` ★INVARIANT★:`_VENDORED_TOOLKIT` 不得含授權檔;本輪只讀 `_VENDORED_ALL`,沒改清單,不影響。
- `Systems/測試假綠形態.md`、`lumos-cli-read.md`、`lumos-cli-lifecycle.md`、`design-loop.md`:本輪改動不碰 search 排序、re-inject、處置閘,不影響。

最高等級:clean
