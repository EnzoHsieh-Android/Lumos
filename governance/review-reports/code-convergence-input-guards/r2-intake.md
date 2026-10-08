# R2 收貨、前後對照與處置

preflight-4: ran

七席fresh read-only xhigh全部交卷後才改source：原報logic major1、architecture major1、resources minor1，其餘clean；同模型家族、未派外家。原報與每席材料完整性收據保留，架構席只有diff新增號引句去除的格式重送，原級別／ID／判準不變。原clean零引句quote rc2為N/A，不造finding來湊通過。

當前pitfalls standard，但原loop high與三輪上限不變。1697行是必讀材料及預留150行上下文的實際計數；檔名索引實際442，派工文字434誤差由席指出、實際全讀442，沒有截斷。原2675全檔告警另歸檔，23條新增行交集只作縮材，不冒稱lint-new。

| ID | 觀察／判準與版本對照 | 處置 |
| state-F1 | HIT：確定性index撤回current f678 rc0/main cc032633 rc1；原R1 4f同型亦rc0，首版借用能力漏網，不是R1修補新生回歸。自然git commit並行未实證，辯方判非blocking hardening | folded：只在讀取前後索引模式/物件/階段/路徑可見差異或首讀失敗時撤回額外test evidence，沿原正式退路；普通/-O先22/2後24/0，穩定index及worktree-only保持rc0 |
| alignment-F1 | HIT：parser OSError修前f678 rc2誤報snapshot讀不到；main原版會吞掉並可成功，辯方以寫入stub查證，因此不是新安全放行回歸。raw major保留，辯方判minor診斷錯誤 | folded：try僅read/decode，parser在外。現場故障注入普通/-O先48/2後50/0，原Runtime與成功帳不變控制保留 |
| key-F1 | HIT：無重用cache mutant原生命週期6/0仍綠；新唯一版本讀數6/2，正確8/0，4/12提交5/13次。R1新增測試的覆蓋缺口，沒有證明修補後產品正常路徑退化 | folded：保留實際存活上限，補重用次數與原壞版翻紅；抽helper後同型mutant再次6/2、正確8/0 |
| lint-F1 | HIT：main mark7、R1原13、f67814；真複雜度增加讓新增告警關卡擋。編排者機械補充，不當第八席 | folded：單group讀取helper6、mark8，原判定層純集合釘保持；不waive真增加 |

兩條raw major沒有洗成clean，仍按原報存檔與記帳；本批採取局部折入，accepted空。乾淨state-defender独立讀程式／Git官方源與重算Ruff：evaluate main52/current52，只因def新增參數換指紋，原指紋已有waiver。精確36c23613f0cfca05新放行、兩個计划留2026-10-20 REVISIT，不改全域指紋演算法或關全閘。defender未重新跑indexcounter（唯讀PermissionError）；index實跑由編排者私有fixture提供，原wrapper解包例外收據留存、不当產品紅。

初次新增index方法在main入口後造成0個測試被選中；移到入口前才實跑22/2。這是測試接入錯誤，原log保留，不算產品缺陷或回歸。

修補後固定CLI57fdf7883ed0dabd9ecb1ad378cc4aa564feb97d0f11559139d0fce0ee91b4e1、test fbe6d14041d598b965f4e53f859528b3b63b429d148123c4168d369cbed8b6df：nodehome完整四片570/0/0，24與8包含；H50與IO24共74/0/0。修前f678的兩支H方法原樣執行修後product，70/0/0，與74重疊不加總。這是本輪前後正常行為保留的實證，不能冒稱全套或真實審查輪數改善。

regression-set: none。state原4f存在；parser main已吞故障，修補只纠正誤診；cache測試盲點不是已證明產品修前正常修後退化；mark複雜度自首版增，f678又增1，屬可追溯機械告警修正而非執行結果回歸。R1曾把reader移入判定層的真正修補回歸由原架構釘543/1攔下、移回後544/0，記在歷史修復與圖譜，不掛到R2不存在的finding上。

使用者2026-10-06進一步要求主軸是當輪修復有無新問題／回歸，兩计划decision-add留痕；R3先看R2補正delta，再對原正常行為及合約。新測試不存在不當作修前紅，也不把新席每項發現都算修補回歸。

R1修正關卡f678 passed且無跳過，原固定全套為下一次source修正停止在10/16片6881/0/0，不称全套綠。12份舊source bundle乾淨clone可匯入並重建d903 ac497，R2來源f678另封存。這些是歷史證據，不当新source全套／交付冷clone。第三輪、固定最新全套、最後bound/kill/anchor/goldens及CI仍待；未push/PR，PR前問使用者，Windows與全圖清帳不擴張。
