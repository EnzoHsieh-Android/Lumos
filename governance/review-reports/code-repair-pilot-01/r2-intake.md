# 修復穩定性試行第1案 r2

正式材料 r2-snapshot.patch 為main2db51cc4至當時index的整條分支差異2891行；超1800按兩席鏡頭分工，另給r1-postfold.patch輔助，未縮成只審修復delta。兩席全收齊後才回退。

| id / 根因組 | 重現與來源 | 改變/保持行為及去向 |
|---|---|---|
| R2C1 / C1-R1 | HIT；grep 'scripts/lumos' README.md及find管線列檔，2db51cc4與候選均true | 原有漏看、原C1未修完整；未折、未放行，轉Issues/探針讀碼證據不足 |
| R2C2 / C1-R1 | HIT；cd scripts && cat lumos，修前true修後false | 修復引入1條；撤回候選恢復原true，避免疊新的shell parser；不是修好R2C1 |

兩條皆major，不降級。編排者與新席分別本機重現相同結果，r2-classification.json凍結三組輸入的前後值。沒有把「原有漏看」計成修復引入。不是同根因連續兩次修復引入，未觸发兩次的硬停條件；此次因修法將擴成新的證據收集/解析機制而主動拆出重設，屬兩輪中止，非達三輪上限。

本案保留3個根因修復組分母（C1嘗試後回退，C2/C3保留草稿），修復引入缺陷1個，原有漏看1個，未新增偏好，待查0。C1新測試自工作樹撤回但在r1-postfold/r2-snapshot內保留；不能以删測試後全綠宣稱C1解決。

原始報告r2-correctness/r2-arch均保存；arch僅由lumos report-normalize --write搬移檔首severity，未改判斷。quote-check全命中、refcheck均存在、seat-check兩份材料均覆蓋。loop next因既有panel委派路徑拒絕新式多席帳，正式輪號依r1帳循序使用r2；未另開編號洗輪次，最終問閘仍用--disposal。

編排者提交前home check指出測試Systems新增說明不屬其認定的改動檔之家（它排除測試檔），移除該新增段，脈絡已在codex-harness與Verification。非production修復副作用，不計入缺陷數。

因帳本API不接受「有finding但未處置」的部分集合，本輪只記原始severity/findings/report/intake，不偽造folded/accepted集合；未處置原因以本表為準。outcome封閉列舉沒有「擴大範圍而中止」，不硬套達上限或爭議分類，原因寫note。最終閘應為FAIL，不寫code-loop pass。

收尾驗證與最終時間見Verification及計劃；本intake入帳後不追加。沒有推送、沒有放行觀測期。
