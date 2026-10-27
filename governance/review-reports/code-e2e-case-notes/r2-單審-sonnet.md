severity: minor

我只用一次性的專案實測,沒找到會讓判定錯誤放行或資料消失的洞,只有一條規格字面和程式對不上的 minor。涵蓋報告測試共 49 支全過,殘留索引的 `-k residual_test_files` 也過。`-k residual` 全組還在背景跑,結果尚未回來,所以殘留索引「完全不變」只能算部分驗證。

### C1 路徑後面接斜線仍算「提到」,與規格寫的「緊貼斜線不算」不符
severity: minor
blocking: 否
引句:「(?![A-Za-z0-9_-]|\.[A-Za-z0-9])")」
歸因:有證據的原有漏查。修前正文比對是裸 `flow in t`,連前後邊界都沒有;這條邊界是修補新加的,規格字面與它從一開始就不一致。
1. 輸入:情境 `login.ok` 的流程檔是 `.maestro/login.yaml`,筆記正文寫 `.maestro/login.yaml/x`。
2. 走到 `_e2e_note_gaps` 的 `seen()`,尾端先行斷言只擋英數、底線、連字號與「點加英數」,沒擋 `/`,所以這句算「提到」,`login.ok` 不列。
3. 我用同一條正規式直接驗過,`.maestro/login.yaml/x` 回 True。
4. 規格〈報告多列什麼〉寫「緊貼英數、底線、連字號、點或斜線的不算」。實務上流程檔後面接斜線不會發生,所以只算 minor。
file: `scripts/lumos:42213`

### 修補驗證(repair)
修前 = 7be6aac1、修後 = 8a3a4643b65e2b782e1bae0266adc42082af25eb。同一支實驗腳本在兩版各跑一次。

- 一個情境列兩支流程檔、只有一支被合約綁到:輸入是 `login.ok` 列 `login.yaml` 與 `other.yaml`,只綁 `[test:ui:login_ok]`。預期不列。修後測試內建此例通過,我也實跑過「只綁 login」的基本例,修後 `cases_without_notes == ['other.x']`。修前行為沒有另外實跑,所以這條只能說修後成立。
- 路徑邊界:用修後的正規式逐字測過。
  - 不算提到:`a.maestro/login.yaml`、`-.maestro/…`、`../.maestro/…`、`路徑/.maestro/…`、`.maestro/login.yaml-v2`,以及實跑的 `.maestro/login.yaml.Next`。
  - 算提到:`見.maestro/login.yaml`、`[.maestro/login.yaml]`、`./.maestro/login.yaml`,以及實跑的 `.maestro/login.yaml.`(句點結尾)。
  - 修前實跑:`.maestro/login.yaml.Next` 會被當成提到(結果 `['other.x']`)。修後正確改列 `login.ok`。
- 流程檔名字改從測試名索引反查:
  - 平台 root 設成 `.maestro`,結果同修前。
  - 平台 root 設成不存在的 `sub`,或設成專案外的 `../zz`,而合約綁了 `login_ok`:修前 `login.ok` 不列、也沒有 stray;修後 `login.ok` 照列,stray 多列 `login_ok`。這是行為改變,但更接近規格,因為平台根底下根本沒有那支流程檔,合約對不到它。
  - 流程檔缺 `appId:`:兩版都是 `login.ok` 照列,另有 stray。
  - 一個檔有兩個 `name:`,只綁第二個:兩版都不列。
- 變異推理:正規式沒有行為變異執行,只讀出 `old/`、`.bak`、`x.` 三個負例都蓋到前後邊界,`./` 開頭的正例蓋到可選前綴。底線與連字號當前綴沒有測試,但取消它們的假想改壞沒有具體失敗場景,不列。

### preserve
- `_residual_test_files` 只是把取名迴圈搬進 `_platform_name_files`,唯一的差別是 `_titled` 從迴圈內移到迴圈外,值不隨檔變,所以行為不變。這是讀程式的結論,另有 `-k residual_test_files` 的 1 支通過;`-k residual` 全組未回來,未判定。
- 既有涵蓋報告的三項和 doctor 那一行:只對照到 `-k android_e2e_coverage` 的 49 支全過,沒有逐項比對輸出。
- 正文寫 `` `./.maestro/login.yaml` `` 與 `流程是.maestro/login.yaml。` 這種中文或標點緊貼的寫法仍算提到,測試內有,我也用正規式驗過。

### 三問
1. 原問題修復效果:有。證據是上面「一情境兩流程檔」與邊界的實跑與正規式結果;修前的證據只有 `.maestro/login.yaml.Next` 一例。
2. 修補處的正常、錯誤與相鄰路徑:
   - 正常路徑(`base-bound`、`root=.maestro`、多名字)修前修後相同。
   - 平台 root 錯誤或在專案外的路徑,修後是上面說的行為改變,偏向更準。
   - `mplats` 為空或平台設定讀不懂時,`pd` 不會被讀到。
   - 兩個 maestro 平台那一例,兩版都是 `login.ok` 照列、stray 為空,我沒查清是我的設定不合法還是原有行為,未判定。
3. C1 這個案例:修前沒有邊界,所以也算提到(同一結果);修後仍算提到。

### 未驗範圍
- 大圖譜與大 yaml 的效能:修後 doctor 路徑會走訪平台 root 底下所有 yaml,我沒有量測。
- 流程檔被符號連結時,`resolve()` 之後與對照表路徑對不上,沒有實測。
- 中文 `name:` 兩版都被當成 stray,是原有行為。

### 暫存
`/tmp/lumos-seat-work/code-e2e-case-notes/單審-sonnet/` 還沒刪。背景測試(任務 bovois35l)還開著該目錄下 `after` 的工作目錄,依規定不能在有程序佔用時刪,只能等它結束再刪。

共 1 條,其中 major 0 條
