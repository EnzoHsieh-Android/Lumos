否決成立
1. 事故主因是紀律未守，不是檢索能力不足：事故自述明載「沒查圖譜就開案」，且既有節點一搜即中；同案亦證實編排者曾跑提示入口卻仍忽略，直接反駁「只是沒看見」的歸因（docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:53、docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:59）。因此 advisory 可能降低偶發遺漏，但不能宣稱命中根因。
2. A 不是可靠入口栓：既有裁定已明載 `loop next` 也只是可能不跑的指令，派工時沒有機械強制點（docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:38、docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:39）。在已有 546 次提醒失效前例下，再加多行提醒缺乏足以翻案的新證據（scripts/lumos:1201）。
3. `loop next` 結構技術上容得下清單：它先組 dict、JSON 整體序列化，文字模式則以明確鍵白名單逐項輸出，新增專用清單分支即可（scripts/lumos:5819、scripts/lumos:5897、scripts/lumos:5899、scripts/lumos:5911）。但現有文字白名單不會自動印新鍵，spec 必須明訂同步修改與各 phase/JSON 回歸測試（scripts/lumos:5911）。
4. B 的插點確實現成：完全同名檢查位於目標路徑算出後，下一步才 `mkdir` 與寫檔（scripts/lumos:9602、scripts/lumos:9604、scripts/lumos:9607）。然而「提醒後照常建、叫使用者確定後再跑一次」在非互動 CLI 中自相矛盾；呼叫者看到提醒時檔案已經建立，不能構成建檔前防撞。
5. 既有多詞回退只吃空白分詞，不會替 CJK 做語意切詞；無空白 CJK 明載「沒有各詞可退」，只能給提示（scripts/lumos:2088、scripts/lumos:2099、scripts/lumos:2138）。BM25F 雖有 CJK bigram tokenizer（scripts/lumos:1871、scripts/lumos:1875），候選回退卻仍是子字串 OR，故 spec 未定義的「CJK 切詞」是承重缺口，不能視為既有能力直接接上（scripts/lumos:2176、scripts/lumos:2178）。
6. 更小且對症的方案是只做 A 的首輪短提示／相關節點清單，不做 B；A 至少出現在派工前，而 B 在不阻擋、不互動的前提下只能事後告知。若不願承擔 CJK 查詢與輸出合約，最小版本可先在 `loop next` 首輪印一行具體 `lumos search "<由 loop-id 拆出的詞>"` 指令，但仍須誠實標為紀律輔助而非根治。
7. 足以否決進實作的缺陷有二：根因論證被事故本身的「提醒已跑仍忽略」反證，且 CJK 查詢生成尚無可實作規格（docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:53、scripts/lumos:2088）。應先縮案並補齊切詞、作廢節點是否納入、文字/JSON 合約及 B 的真實時序語意，再送審。
severity: major
