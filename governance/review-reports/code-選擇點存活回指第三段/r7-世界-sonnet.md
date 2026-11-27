severity: major

## w1 帶說明後綴的「## 驗收條款(…)」標題在 repo 裡有 4 篇真實計劃,整節驗收條款被當成計劃正文
severity: major
blocking: 是

引句:「_h2_section_lines(text, rx, spans=spans)」
來源:https://spec.commonmark.org/0.31.2/
file: `/Users/enzo/harness/lumos-reach3/governance/review-reports/code-選擇點存活回指第三段/r7-repair.patch:247`

找節用 `^##\s+驗收條款\s*$` 比整行,後面多一個字就不算讀取器的節。repo 裡有 4 篇計劃是這樣寫標題的:
- 逃逸自動記_計劃
- 雙向門放行_計劃
- 規格落成可驗收條件_計劃(兩篇,各有「(半套;…)」「(2026-09-17 落地版;…)」這類後綴)

重現:對 `逃逸自動記_計劃.md` 呼叫 `_choice_plan_sections`,得到段名 `〈驗收條款(全部有真測試、綠)〉`。段內第一行是 `- [S1] 當代碼審記下的發現裡有一條型是 code…[test:t_escape_auto_from_code_loop]`。同一份文字用 `clause_bindings` 讀,S1 到 S9 都是 defined 條款(第 74 行起)。所以條款定義行、測試名和條款旁的說明文字,同時留在條款和計劃正文兩邊。

雙向門放行那篇有 30 條,規格落成那篇有 17 條,一樣是這個狀況。

補充:r7 snapshot 第 4098 行的註解寫明「讀取器讀不到的帶說明標題留在正文」,看起來是刻意的取捨。但 `clause_bindings` 並不依賴標題字面,取捨的前提(內容至少有一邊看得到)成立,代價卻是正文被灌入條款原文,正文那一邊就不乾淨。

## w2 驗收條款節內含 HTML 註解包著的標題時,註解後面的條款內容漏進正文
severity: minor
blocking: 否

引句:「if ln.startswith("#"):」
來源:https://spec.commonmark.org/0.31.2/
file: `/Users/enzo/harness/lumos-reach3/governance/review-reports/code-選擇點存活回指第三段/r7-repair.patch:136`

CommonMark 的 HTML 區塊(`<!-- … -->`)裡的 `## 舊節` 不是標題。`_visible_lines` 的說明寫明不偵測 HTML 註解,於是 `_h2_section_lines` 把它當標題。

重現輸入:`"## 驗收條款\nC1 條款一\n<!--\n## 舊節\n-->\nC2 條款二\n"`。
- spans 是 `[(1, 3)]`,讀取器只拿走到 `<!--` 為止。
- `_choice_plan_sections` 回 `[('〈舊節〉', '-->\nC2 條款二')]`,C2 條款二進了正文。

反向也會:`<!--\n## 驗收條款\n-->` 會讓註解後面的正文被扣掉(重現:`"## 範圍\nA\n<!--\n## 驗收條款\n-->\n正文B\n"`,正文B 消失)。

實務上 repo 的 Projects 目錄裡沒找到「註解包標題」的寫法,所以降為 minor。

## w3 縮排 1 到 3 格的標題、Setext 標題、`##\t`、空的 `##`,對讀取器是「不結束節」,正文內容會被吞掉
severity: minor
blocking: 否

引句:「elif ln.startswith("## ") or ln.startswith("# "):」
來源:https://spec.commonmark.org/0.31.2/
file: `/Users/enzo/harness/lumos-reach3/governance/review-reports/code-選擇點存活回指第三段/r7-repair.patch:144`

CommonMark 規格的對應條文如下:
- ATX 標題可以有最多 3 格縮排。
- 結尾 `#` 序列可有可無。
- 空標題合法。
- Setext 標題是 `文字` 加 `---` 或 `===`。

重現,都是驗收條款節後面緊接一段本該屬於正文的內容:
- `"## 驗收條款\nC1\n ## 後續設計\n正文B\n"`:`_choice_plan_sections` 回 `[]`,正文B 被整段扣掉(兩邊都看不到正文B,只有讀取器那邊有)。
- `"## 驗收條款\nC1\n\n後續設計\n--------\n正文B\n"`:spans 是 `(1, 6)`,正文為空。
- `"## 驗收條款\nC1\n##\t後續\n正文B\n"` 與 `"…##\n正文B\n"`:同樣整段吞掉。
- 反方向:`"## 驗收條款 ##\nC1 條款一\n## 後\n正文\n"` 的整節驗收條款進到正文,段名 `〈驗收條款〉`。

repo 的 Projects 目錄裡,縮排的 `#` 開頭行只出現在程式碼片段的註解,沒有縮排標題、也沒有 `## 驗收條款 ##`,所以是 minor。規格註解已說明 r2 是刻意只認 ATX。
備註:445 個檔含 `---` 行,多半是分隔線或 frontmatter。我沒逐個確認哪些緊接在文字行後面。

## w4 容器內的圍欄與非標準圍欄標記
severity: minor
blocking: 否

引句:「_CHOICE_HEAD_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")」
來源:https://spec.commonmark.org/0.31.2/
file: `/Users/enzo/harness/lumos-reach3/governance/review-reports/code-選擇點存活回指第三段/r7-repair.patch:228`

CommonMark 說:沒有收尾圍欄的程式碼塊,會在外層引用或清單項結束時關閉,不是延伸到文件結尾。

`_fence_regions` 只看行首縮排 ≤3 的 ``` 與 ~~~,有兩處對不上規格:
- 清單項或引用裡縮排 ≥4 格的圍欄不認,不過 4 格縮排內的內容本身帶縮排,不會誤判成標題。
- 反引號圍欄的資訊字串含反引號時,規格說這不是圍欄,這裡當成圍欄。

我試了「``` a`b」,然後 `"## 驗收條款\nC1\n``` a`b\n## 後\n正文B\n"`:`## 後` 被當圍欄內容吃掉,正文B 消失。

這些寫法在 repo 計劃裡實務上不會出現,所以是 minor。未閉合圍欄把驗收條款節延伸到檔尾,規格自己也是這樣,不算缺陷。

## w5 方向:世界上更可靠的既有做法是「先解析成語法樹、再按深度切節」
severity: minor
blocking: 否

引句:「elif ln.startswith("## ") or ln.startswith("# "):」
來源:https://github.com/wooorm/mdast-util-heading-range
file: `/Users/enzo/harness/lumos-reach3/governance/review-reports/code-選擇點存活回指第三段/r7-repair.patch:144`

mdast-util-heading-range 的定義是:節從匹配標題起,到下一個同深度或更淺的標題,或到文件結尾。它吃的是 CommonMark 解析後的樹,所以 Setext、縮排標題、HTML 區塊、容器內圍欄全部由解析器處理,不是用正規式再補。

我們的做法在二級節上效果相同(遇到 `# ` 或 `## ` 結束),差別有兩個:
- 標題判定靠逐行正規式,不是語法樹,所以 w2、w3 那幾個邊界要靠逐條補。
- 標題字面匹配讀取器,和世界做法的「按位置切、再比標題文字」不同。

零依賴的家規下不能引入 markdown-it 或 mdast,所以建議是在 `_visible_lines` 這一個共用處補 HTML 註解、1 到 3 格縮排與 Setext 的判定,不要在 `_h2_section_lines`、`_choice_plan_sections` 兩處各補一套。本輪只寫觀察。

## 附:查了什麼
- 查詢詞:CommonMark 0.31.2 規格全文(ATX 縮排、結尾 `#`、空標題、Setext、容器內圍欄的關閉規則);「mdast-util-heading-range section until next heading of same or lower depth」。
- 讀過的來源:https://spec.commonmark.org/0.31.2/ (只讀到前 100000 字,涵蓋區塊結構與標題章節);mdast-util-heading-range 的 README 與 npm 摘要。markdownlint、markdown-it、mistune、Python-Markdown 的 toc 沒有深入查。
- 實測:在 `/tmp/lumos-seat-work/code-選擇點存活回指第三段/r7-世界-sonnet/` 用 SourceFileLoader 載入 `/Users/enzo/harness/lumos-reach3/scripts/lumos`,跑了 20 個案例,以及 3 篇真實計劃(逃逸自動記、雙向門放行、規格落成可驗收條件)。
- 沒有造成問題的案例:CRLF 結尾、不換行空格或全形空格的標題、H3 不結束節、H1 結束節、跳脫的 `\##`、引用裡的標題、預期值表表格、圍欄內縮排標題。
- 沒跑:全套測試,也沒用 `python3.14 scripts/test_lumos.py -k` 驗證 `_choice_plan_view` 之後的層判讀行為。
- 鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/4d0ef31564155a2ce9aaadc3f0981b99270a5228cbf5ec83125b88e21ed4df6e.json.warming` 不存在,沒有要處理的鎖。
- 暫存目錄 `/tmp/lumos-seat-work/code-選擇點存活回指第三段/r7-世界-sonnet/` 留著,由編排者收貨後刪。

總結:最高等級是 major
