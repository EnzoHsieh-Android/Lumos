severity: minor

第七輪(正確性・修補鏡頭)報告。我實跑了 `dispatch-lens main..HEAD --arch-target`(代碼審)與 `--spec ... --arch-target`(設計審),另外用 `_arch_target_lens_split` 量了時間。實驗在 scratchpad 的 `cr-lr7-正確性/`,沒有碰 lens-repo。

### Finding 1:按節點分配的字數不含標題行,第三個節點會整篇被整段上限截掉

severity: minor
blocking: 否 — 截斷時尾巴有「(已截:…後面的沒附)」提示,只是目標規則沒送到審查席,審查降成照鄰居審,不會靜默錯判。
引句:「per_node = (_LENS_SPEC_TEXT_MAX - 2000) // max(1, min(len(targets), _ARCH_TARGET_LENS_NODES))」

問題:`per_node` 只限制規則原文的字數(`used` 只累計規則行),每個節點的標題行不計入。標題行最多列 20 支檔名,每支包 ‹› 後常見 90 到 130 字,單行可到 2000 字以上。三個節點的「標題加規則」合計超過 12000 字時,最後那道整段上限從尾巴截行。這正是這輪說要避免的「後面節點整篇消失」,只是搬到了標題行這一側。

具體失敗情境:
- 輸入:3 個目標節點,各命中 20 支路徑約 95 字的檔(例如 `app/m2/src/main/java/com/example/application/feature3/ui/FeatureScreenViewModel3.py`),每個節點 30 條約 120 字的規則。
- 結果:第三個節點 `Systems/N2` 的標題和全部規則都不在輸出裡。輸出只剩 N0、N1,以及 `(已截:附加段超過 12000 字,原本 15393 字,後面的沒附)`。
- 對照:規則縮到 12 條、每條約 80 字時總長 11980,三個標題全在,所以這是接近上限才發生。
- 影響:N2 的檔在報告裡沒有「目標規則」可引,但提示又寫「段外的檔照鄰居審」,審查席會把它當鄰居審。
- 修法方向:`per_node` 要先扣掉標題行長度,或把標題行也納入 `used`。

佐證:``file: `scripts/lumos:44387` ``、``file: `scripts/lumos:44413` ``(`_arch_target_node_lines` 的 `used` 從 0 起算且不含標題行)

### Finding 2:規則原文走名字出口後,反引號和反斜線被轉成 `\u0060`、`\u005c`,審查席抄不回原文

severity: minor
blocking: 否 — 只影響可讀性和「目標規則:「<原文 ≥10 字>」」的抄寫,沒有程式碼去比對引句,不會誤擋或誤放。
引句:「ln = f"  - {_arch_target_show(text, _ARCH_TARGET_RULE_SHOW)}」

問題:規則原文改用 `_lens_author_name_show`,`_LENS_NAME_ESC_CHARS` 含反引號和反斜線,規則行裡的程式識別名都被轉義。實跑輸出是 `‹RULE:\u0060ViewModel\u00600-0 不得 import \u0060android.view\u0060 之類 …›`。

具體失敗情境:
- 輸入:規則 `` `ViewModel` 不得 import `android.view` ``,Android、Kotlin 專案的規則常這樣寫。
- 結果:派工詞裡是 `\u0060ViewModel\u0060 不得 import …`。
- 審查席依指示抄 ≥10 字進 finding 時,有兩種抄法,和筆記原文都對不上:抄轉義後的字,或猜著還原。
- 另外每條規則上限 200 字包含尾巴的 `[依據…][since…][retire…][until…]` 欄位,實質規則句約剩 110 字,長句會被截。這點在舊版沒有。

佐證:``file: `scripts/lumos:44417` ``

### 已讀,無 finding

- **一般使用格式**:檔名、節點名、規則都包 ‹›。標題帶檔數(`(20 支檔)`),下面一條規則一行,段頭尾有注入框,尾端固定一句目標規則指示。照目標規則審的檔清楚,可讀。
- **「只算到一半」誤報**:正常規模不會觸發。
  - 條件是改動檔超過 2000、宣告超過 500、或超過 5 秒。
  - 量測:300 檔乘 30 條花 0.01 秒;2000 檔乘 500 條,簡單樣式 0.53 秒,`**/x/**/*.kt` 型樣式 1.37 秒,都沒有觸發 cut。
  - 邊界用 `<` 判斷,剛好 2000 或 500 不會誤報。
  - 觸發時只有警告行,沒有也不亂印。
- **推送前分級**:`scripts/lumos:45231` 那條呼叫 `_arch_target_split(_at_files, _at_rules)`,新參數全是預設 `None`,照舊全算,沒被上限影響。
- **按節點分配後的標題與計數**
  - 前 3 個節點各自保住標題。
  - 第 4 到 23 個節點只列名,再多的印「另有 N 個目標節點沒列名」,計數是 `len(targets)-3-20`,算式正確。
  - 規則用完分配時印「另有 `len(rules)-j` 條沒貼」,把超過 30 條的部分一起算進去,正確。
  - 設計審的 `listed`、`shown` 是依截斷後標題行還在不在來數,`text_truncated` 照實。
  - 實測 `--spec` 路徑正常。
- **資料狀態五問**
  - 空:只有警告或只有 cut 時會印段,收尾那句指示照附。
  - 單一節點:`per_node` 約 10000,正常。
  - 多節點:見 Finding 1。
  - 邊界:2000 檔與 500 條剛好不觸發。
  - 髒資料:特殊字元走出口,`─` 被轉義,框內不會因 `─────` 被丟行。
- **掛鉤**
  - `_framed_note` 的 NOTE 與 TAIL 拆分後,`.format` 參數對得上。多餘的 `cmd` 和 `n` 參數已拿掉,沒有殘留呼叫。
  - `_spec_name_show` 與 lumos 的 `_lens_name_blank` 邏輯一致,空字串回「(空名字)」。
  - 8 碼跳脫兩邊一致。
- **spec-freeze**:一般路徑(含空白、中文)`_lens_name_esc(rel)==rel`,那行仍可直接貼。只有含特殊字元時才改印跳脫版,並加 stderr 提示。我沒查到有程式讀 spec-freeze 的 `spec_path` 欄位。
- **對外 API 相容(be-api-compat)**
  - 設計審 `--json` 的 `listed`、`shown` 語意改成實際印出數,新增 `text_truncated`,是加欄位。
  - `listed`、`shown` 截斷時會比舊值小。掛鉤與 `scripts/lumos` 內沒有找到讀這兩欄的地方。
- **授權(be-authz)**:這輪沒有新增端點,不適用。

最高等級 minor,blocking 0 條。
