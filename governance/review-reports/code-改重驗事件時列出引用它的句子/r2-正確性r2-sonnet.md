severity: minor

我看到的圖譜材料:LUMOS-IMPACT 只給了範圍,尾端沒有附固定席筆記,也沒有「算不出來」的說明,所以我沒逐條判固定席。角色卡也沒附,略過。

## F1 同一句裡重複出現的連結,讓同一句被列兩次
severity: minor
blocking: 否
引句:「for m in _RVB_RE.finditer(raw):」
佐證:file: `scripts/lumos:4165`(`_revalidate_backref_lines`,在 a040f829 的樹上)
失敗場景:
- 輸入:Projects/A.md 有一行「[[Verification/X]] revalidate_when 與 [[Verification/X]] revalidate_when。」。這是一句話,裡面有兩個各自連到 X 的 `[[X]] … revalidate_when` 配對。
- 路徑:`finditer` 對這一行產生兩個互不重疊的比對。每個比對都往前找到同一個 `head`、往後找到同一個 `tail`,於是 `out.append` 兩次,內容完全相同(來源篇、行號、原句都一樣)。
- 後果有兩個。清單上同一行同一句印兩筆。標頭「有 N 句」的 N 被灌水,實跑是 26,實際只有 25 句不重複。灌水的 N 也會讓「最多 20 句」的名額被重複項佔掉,擠掉真正不同的句子。
- 這個只有「配對各自完整」的寫法會觸發。「[[X]] 與 [[X]] 的 revalidate_when」不會重複,因為第一個連結不能跨過第二個連結(`_RREF_NOT_END` 排除 `[`),只有第二個連結比對得上,實跑只列一筆。
歸因:有證據的修復回歸(上輪修補「拿掉取到就停」引入)。修前每行最多一筆,所以同一句只會列一次,但同一行第二句被漏掉(這是上輪要修的問題)。修後同一行的每個比對各一筆,同一句被重複列。
查證命令與結果:
- 在 /tmp/lumos-seat-work/code-改重驗事件時列出引用它的句子/正確性r2-sonnet/v 建了兩篇筆記:A 是上述三行,其中第 8 行是重複案例;B 是 21 個不同的句子。
- 修後 a040f829:`python3.14 c/scripts/lumos set Verification/X revalidate_when "新事件"` 輸出「有 26 句」。`Projects/A.md:8` 同一句連列兩行。
- 修前 7a9b5d0d:同樣的庫輸出「有 24 句」,`A.md:8` 只列一筆。第 9 行有兩句都指向 X,修前只列第一句,這就是 r1 的漏列。
- 修法:`out` 去重,例如以 `(src, no, 句首位置)` 為鍵。

## 已驗主張
- 同一行三句、其中兩句指向 X、一句指向別篇 Y:修後列兩句、不列 Y 那句(A.md:9),取到就停的漏列已修好。
- 20 句、21 句的邊界:B 篇 21 個不同句子加上 A 篇的句子,輸出剛好 20 筆後印「…還有 N 句」。標頭的 N 受 F1 影響而不準,上限本身沒問題。我沒有單獨跑「剛好 20 句」「剛好 21 句」的純淨庫,只確認了大於 20 時只印 20 筆。
- 新事件清單印的是寫入後從磁碟重讀的值(「新事件」)。
- 測試:`-k set_revalidate_when` 13 過 0 敗;`-k s21_revisit_ref` 30 過 0 敗。
- `try` 只接 `OSError/ValueError/RuntimeError/UnicodeDecodeError`,`TypeError` 之類寫錯程式的例外不會被吞成靜默,會直接丟出。同一個 `except` 會吞掉掃描裡出現的 `ValueError`,這是照 `_drift_print_backrefs` 的既有做法,可接受。

## 未驗範圍
- `set` 失敗時不印:只讀了 `main` 裡的 `rc == 0` 條件,沒有實跑失敗路徑。
- 標頭印完後,重讀新清單遇到 `OSError/UnicodeDecodeError` 會無聲 `return`。結果是只有句子清單、沒有「這篇現在的 revalidate_when」,stderr 也沒有任何說明。我想不出實際會發生的輸入,只是看到程式這樣寫,沒有實跑。同一段讀檔若丟 `ValueError`,不在那個 `except` 內,會在寫入完成後把例外丟出。
- 同名不同資料夾的解析漏列已在計劃的天花板 3 寫明,我沒有重驗。

總結:修補把同一行多句各列一筆的目的達成了,但同一句裡出現兩組完整配對時,這一句會被印兩次,「有 N 句」的數字被灌水,而且重複項會佔掉 20 句名額;是小問題,不擋推送,建議在收集時去重。
