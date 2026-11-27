severity: clean

我把修補差異(`r4-repair.patch`)的 `scripts/lumos` 部分逐段讀過,沒有跑測試。這個環境沒有 `timeout` 指令,我也沒另外重跑 `-k choice_layer_plan_sides` 與 `-k choice_layer_template`,以下結論都來自讀程式。

三個問題的結論如下。

- **加總有沒有守住**:`_choice_layer_plan_sides` 依大小由大到小改成旁檔,直到內嵌加總小於等於 `_CHOICE_LAYER_SHARED_MAX`(100KB)。它是以整組(主計劃或未歸計劃)出現過的全部計劃來算。每一份只含該組存活的子集,所以每份實際內嵌的計劃加總必定小於等於 100KB。
- **一份的上限**:存活自己的材料另外受 `_CHOICE_LAYER_PART_BYTES`(200KB)限制。一份總量最多約 300KB,加上指路與段名清單的少量固定開銷,這與規格〈範圍〉8 的分開算寫法一致,沒有超出。
- **重複寫旁檔**:`_choice_layer_side` 用「清單編號 + 計劃路徑雜湊」命名,每份計劃對應一個固定路徑。`_choice_layer_split_groups` 用 `sides.update(g)` 合併各組結果,所以同一計劃在多組都被外移時也只有一個鍵、只寫一次。
- **邊角行為**:某計劃在 A 組被外移、在 B 組因為小而內嵌,兩邊各自一致,只是少量冗餘,不算錯。
- **渲染次數**:`_choice_layer_groups` 在 `_choice_layer_split_groups` 只呼叫一次。每組的 `_choice_layer_plan_md` 大小計算一次,每份渲染時再算一次內嵌計劃,都是線性。
- **修補有沒有引入新問題**:沒看到會做出錯行為的東西。段名清單是新加的內容,只在外移計劃上出現,量很小。
- **同類位置**:`_choice_layer_template` 已改成先分組、再寫旁檔、再寫各份;`_choice_layer_write_parts` 每份帶自己這組的旁檔。我沒找到仍沿用舊的整份清單共用 `sides` 的位置。

總結:最高等級是 clean
