severity: clean

**1. 結構與位置跟鄰居一樣嗎?** 一樣。
- 改動都在 `android_scene` 裡原有的位置:輸入框副標、`layers` 清單的 `sub` 欄、`desc`。沒有新增場景、元件或 `data-kind`。
- `layers` 的元組形狀 `(y,n,label,sub,tag,c)` 不變,中英用 `if en else` 並列的寫法也不變,跟 `assets/readme-diagrams/generate.py` 其他場景相同。
- 兩張 SVG 是用產生器重產的:提交 b8c0107f 同時動了 `assets/android-e2e-en.svg` 和 `assets/android-e2e-zh.svg`,沒有只手改 SVG。
- 家節點 `Systems/README圖產生器.md` 的歷史紀錄寫在既有的 2026-10-25 android-e2e 那一條尾端。該條前幾輪(r1 到 r4)本來就是這樣續寫的,沒有另起一條。

**2. 寫法跟鄰居一樣嗎?** 一樣。
- 英文副標用 `·` 分隔(`dumpsys · Perfetto · logcat per run`),`generate.py:371` 的 `"Update · recheck · mark stale"` 也這樣寫。中文用「、」,同一行的 `"更新、重驗,或標示過時"` 也一樣。
- 識別名、字型大小參數(`16 if en else 17`、`15 if en else 16`)沒動。
- `desc` 照舊是長字串接 `if en else (…)`,中英內容對得上,措辭照 README 正文的「各層用的工具一覽」(`README.md:326`、`README.en.md:326`)。工具名也跟 README 一致:`trace_processor`、`heap_profile`、`java_heap_dump`、dumpsys(`README.md:332`),logcat 見 `README.md:337`。
- 歷史紀錄用 `2026-10-25:`、白話、逗號串接,跟同檔 10-09、10-10 的寫法一致。

**3. 有沒有引入第二種做法?** 沒有。
- 沒有手改 SVG,也沒有第二套元件。
- 文件跟實際對得上:紀錄裡寫的「各層副標改成點名工具、記憶體收集框寫 dumpsys、Perfetto、logcat、替代文字同步」,跟 diff 內容一致。
- 舊副標 `Open/close a screen` 和「反覆開關畫面：記憶體與閃退」在 diff 裡被換掉;專案中其餘位置沒有殘留。

不對齊共 0 條,其中重大 0 條
