severity: minor

我沒有在派工尾端看到「lumos 自動附加」段,所以沒有逐條判固定席筆記;派工只給了 LUMOS-IMPACT 範圍。角色卡開關是 on,但尾端沒有附卡,所以略過。

測試在凍結版 7a9b5d0d 的乾淨 clone 跑過:`-k set_revalidate_when` 10 支全過,`-k s21_revisit_ref` 30 支全過。`_in_spans` 提成共用後,S21 行為沒變。

## F1 同一行指向同一篇的第二句被漏列
severity: minor
blocking: 否
引句:「                    out.append((src, no, raw[head:tail.end() if tail else len(raw)].strip()))」
佐證:file: `scripts/lumos:4160`(提交 7a9b5d0d 的 `_revalidate_backref_lines`;`out.append` 後面緊接 `break`)
失敗場景:
- 輸入:Projects/P.md 同一行寫「甲 [[Verification/X]] revalidate_when 第一;乙 [[Verification/X]] revalidate_when 第二。」
- 執行:`lumos set Verification/X revalidate_when "新事件"`。
- 結果:只列出第一句「甲 … 第一;」,第二句「乙 … 第二。」被漏掉。
- 原因:`out.append` 之後的 `break` 讓每行只取第一個命中。
- 同樣的行為出現在「`[[Verification/X.md|別名]]` 的 revalidate_when 觸發;又 `[[Verification/X#錨]]` 的 revalidate_when 再觸發」。第二句也沒列。
- 影響:計劃筆記說要「列出連到被改那篇、同一句講到 revalidate_when 的句子」,輸出的句數(「有 N 句」)因此比實際少。
查證命令:
`python3.14 /tmp/lumos-seat-work/code-改重驗事件時列出引用它的句子/正確性-sonnet/c/scripts/lumos --vault <放兩句同行的臨時庫> set Verification/X revalidate_when 新事件`
我造的庫在 `/tmp/lumos-seat-work/code-改重驗事件時列出引用它的句子/正確性-sonnet/v`。實測第 9 行、第 10 行各只列一句,第 10 行的第二句沒出現。

## F2 同名不同資料夾時,短名連結會被認成別篇而漏列
severity: minor
blocking: 否
引句:「if not _in_spans(hidden, starts, m.start(1)) and env.resolve(link_target(m.group(1))) == rel:」
佐證:file: `scripts/lumos:665`(`resolve` 的短名回退取 `hits[0]`)
失敗場景:
- 輸入:庫裡同時有 Verification/X.md 與 Systems/X.md,Projects/P.md 寫「由 [[X]] 的 revalidate_when 觸發。」
- 執行:`lumos set Verification/X revalidate_when …`。
- 結果:`env.resolve("X")` 以字典序取到 Systems/X,與 rel 不等,這句沒被列出。
- 對照:我把 Systems/X.md 刪掉後,同一句就被列出(第 8 行出現)。
- 反方向的誤認:`[[Projects/X]]` 指向不存在的檔時,`resolve` 會回退成主檔名比對,這時 `Projects/X` 與 `Verification/X` 會被當成同一篇。
- 歸因:這是既有 `env.resolve` 的行為,不是這個提交新造的,但新功能繼承了它。
- 影響:只有庫裡有重名筆記時才會漏列,算低風險。
查證命令:同 F1 的庫,先放入 Systems/X.md 再跑 set,對照刪掉它之後的輸出。

## 逐項檢查結果(沒找到問題)
- set 失敗時不會印:
  - `cmd_set` 回傳不是 0 就不呼叫列出函式,條件是 `rc == 0 and args.key == "revalidate_when"`。
  - 無值、空字串、含換行的值都在 `cmd_set` 之前或之內被擋,沒有多印。
  - 唯讀檔案我試了 `chmod 444`,仍然 rc=0 並印出列表。這是 `cmd_set` 既有的寫入行為(原子替換),不是新增的問題。
- 多個值、短名、`.md`、`|別名`、`#錨點`:
  - 多值整欄換時,新清單照印。
  - 後三種寫法都對得上。
  - 被改的那篇自己(`src == rel`)有排除。
- 切句:
  - 句首、句尾、整行沒有句尾的切法都對。
  - 前一句的句尾符號會被正確截斷,例如「別名:前面。由 …」只印「由 … 觸發;」。
- 輸出注入:
  - 行內的 ESC 與 BEL 在輸出裡被 `_esc_clean` 清掉了。
  - 來源篇名和事件清單也都過了 `_esc_clean`。
- 效能:
  - 每篇先用 `"revalidate_when" not in text` 過濾,多數筆記不會再往下跑。
  - 我沒有量 760 篇圖譜上的實際時間,只確認程式結構是這樣。

總結:這次改動大致正確,只有兩個小毛病。一行裡有兩句指向同一篇時只會列第一句;庫裡有同名不同資料夾的筆記時,短名連結會漏列。兩者都不會影響寫入,也不會壞掉既有的 S21 檢查。
