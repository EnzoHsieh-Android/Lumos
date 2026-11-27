severity: minor

severity: minor
blocking: 否
scripts/lumos `_choice_layer_plan_sides` 與 `_choice_layer_split`(補修差異,`_choice_layer_render` 附近):每份材料的總大小仍可能超過 `_CHOICE_LAYER_PART_BYTES`。我讀程式碼推論出來,沒有實跑重現(未能重現,自降一級)。

- 失敗場景:`_choice_layer_split` 的 `size()` 只算存活自己的材料,不含共用計劃材料。
- 每份計劃只要共用材料不超過 `_CHOICE_LAYER_SHARED_MAX`(100KB),就整份附進每一份材料。
- 一份材料涉及 k 個計劃時,每份大小約為 k × 近 100KB 加存活材料,可遠超 200KB。
- 「未歸計劃」那組的涉及計劃是 `list(live)`,即全部存活計劃,每份都全帶。
- 例如 5 個計劃各 90KB:每份約 450KB 加存活材料,份數乘上去,工作目錄總量約為份數 × 450KB。
- 補修後只守住單一計劃的共用材料上限,沒守住整份大小與總磁碟量。
- 建議:`_choice_layer_plan_sides` 改成累計各計劃共用材料,總和超過上限就從最大的開始改存旁檔。

引句:「份上限只拿存活自己的材料比:size(存活清單) 是那幾個存活的材料位元組數」

資源面其他檢查,補修都守住:

- **`_choice_layer_render` 呼叫次數:** 每個存活在 `size()` 裡渲染一次(`memo` 快取),分份後每份渲染一次,存活材料約 2 次,不是二次方。
- **旁檔數量:** 每份計劃至多一支,整份清單共用,不隨份數增長。
- **旁檔清理:** 旁檔放在 `choice-layer/` 底下,由 `_choice_layer_prune` 依 14 天清掉,不會無限長大。
- **單一存活很大:** 該份只放它一個並印 stderr 提醒,不會無窮迴圈。
- **版面一致:** 旁檔內容與指路內容由同一個 `_choice_layer_plan_md` 產生,版面一致。
- **`size()` 反覆呼叫:** 在 `while n > 1` 的減半迴圈裡反覆呼叫 `size()`,但有 `memo`,成本是 O(n log n) 的加總,可接受。

總結:最高等級是 minor
