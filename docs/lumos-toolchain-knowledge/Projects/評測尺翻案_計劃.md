---
type: project
summary: |-
  FLAG:DECISION
  KEY:地基盤點第 1 批案 B——檢索評測「未標=0」的尺翻案:Enzo 2026-08-26 裁推翻 08-17「不改尺靠補標」裁定,改 condensed 主尺(計分前剔除未標,於已判子列表算 P@8/nDCG;Sakai 2007)+覆蓋率誠實線;補標管線不拆(condensed 解懲罰、補標解池不完整,TREC 實務並用)
  KEY:[S1] condensed 主尺 [S2] coverage 誠實線+低覆蓋標弱證據 [S3] metric_rev 版本化+雙報過渡至下次 repin [S4] 補標管線不動
  DEP:[[Projects/標註刷新_計劃]]｜[[Projects/地基盤點2026-08-26_調研]]｜[[Systems/graph-sync-coverage]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
decisions:
  - content: Enzo 裁(2026-08-26):推翻 2026-08-17「指標語意不改、靠 delta 補標消滅未標」的刻意不做,真的修尺——condensed 計分為主尺方向,細節過設計審
    id: d1
    context: 地基盤點案 B 踩點發現「該修尺」判定與標註刷新計劃的刻意不做相撞,攤牌後 Enzo 選翻案
    why_chosen: 補標管線治池不完整但治不了懲罰結構:每個提升召回的改動都先被未標=0 扣分,要等人補標才平反——尺本身歪,量測回饋慢一拍;IR 界對不完整判定有成熟指標解,不必自扛
    decided: 2026-08-26
    valid: true
---

# 評測尺翻案_計劃



PRIOR-ART: borrow——IR 界對「判定不完整」的成熟解:①condensed-list 計分(Sakai 2007:計分前把未標文件從排名剔除,於「已判子列表」上算 P@k/nDCG,對不完整判定的鑑別力實測優於 bpref)②bpref(Buckley & Voorhees 2004,只看已判相對序)③infAP(Yilmaz & Aslam 2006,抽樣估計)④RBP residual(Moffat & Zobel:分數旁附「未標最多還能貢獻多少」的不確定帶)。選 ①+④ 的 coverage 簡化版:condensed 主尺+覆蓋率誠實線;補標管線(TREC pooling 增補)不拆,兩者互補。

## 現況事實(2026-08-26 實查)
- `_labels_of`(retrieval_eval.py:101)把 final=None 收斂成 0,★計分專用★註解明寫這是刻意的;08-22 消融實錘:改動讓未標從 4 變 9,分數被系統性壓低。
- 08-17 裁定理由=「改尺則數字與整本 history 全失效」——翻案設計必須正面解 comparability。
- 未標判定已有獨立三態原語(collect_unjudged;「S0」是 [[Projects/標註刷新_計劃]] 的條款編號,指其評測母體定義,與本文 [S1]-[S4] 無關),補標管線(delta/repin+週考卷 S4 訊號)已上線。

## 條款
- [S1] condensed 主尺:**全部品質尺**改在「剔除未標後的已判子列表」上計——search 面 nDCG@5/MRR/Recall@10(主閘是 nDCG@5 不是 @8;漏了它翻案理由在 search 面就沒解掉)、edit 面 P@8/nDCG@8(hook P@top_k 在 code 裡就是 fusion P@8 同一個數字,不是第三個尺)、held-out lift。未標不再=0。實作注意:「未標→0」的收斂在兩處——_labels_of 內部(final=None)與呼叫端 lab.get(n, 0)(根本不在 labels 的節點),單改一處不夠,要換三態介面+兩個呼叫端(retrieval_eval.py:339/:382)的排名剔除。must-see 棘輪(比個數不截 k)與數量閘不受波及、不動。
- [S2] coverage 誠實線:每題附 top-k 已判覆蓋率;整卷 coverage 低於門檻(暫 0.5,首輪實測後定)時 gate 結論標「弱證據」不轉綠——condensed 的已知偏差(愛撈未標的系統會被高估)用覆蓋率+補標對沖。
- [S3] 指標版本化與過渡:history 列加 metric_rev;舊列凍結不重算;過渡期雙報(舊尺+新尺同印)直到下次 repin,gate 門檻在雙報期末重錨。
- [S3b] 固定席噪音閘**維持**「未標=噪音」語意:pin_noise 是固定席策展品質的訊號(席位理應被判過,沒判過就該進補標),不是檢索排序尺——condensed 不適用於它,兩者語意刻意分家(排乾抓到的矛盾在此明裁)。
- [S3c] 消融前置閘(--ablation rc3)退場:它擋人的理由「未標一律算 0、消融比較不公平」被 [S1] 整個抽掉;condensed 上路後消融比較在已判子集上成立,rc3 閘改由 [S2] 的 coverage 弱證據標記接手。
- [S4] 補標管線不動:delta 補標照跑(condensed 解「懲罰」,補標解「池不完整」,TREC 實務兩者並用);標註刷新計劃那條「未標率超線→delta 表+LINE」的週考卷訊號(該計劃編號 S4,與本條撞名純屬巧合)照發。
- 邊界:Landmark 考卷 edit 題庫 n=1、帳上連紅 4 次(08-05/12/19/26)另立 Issue 留該專案;評審/人閘不動;LLM 不進計分迴圈維持。

## 驗證計劃(行為斷言)

- [S1]:合成 fixture——排名 [未標,判2,判0,未標,判1] 取 @2:condensed 後列表=[判2,判0],P@2=0.5(舊尺=0.0);search/edit 兩路徑各一組;未標全剔除後空列表→該題分數記 None 並計入 coverage 而非當 0。
- [S2]:coverage=top-k 內已判比例逐題輸出;整卷 coverage<門檻 → gate 輸出帶「弱證據」字樣且不轉綠(fixture 逼出)。
- [S3]:history 新列含 metric_rev;雙報期輸出同時含新舊兩行(字樣可 grep);舊列不被改寫(檔案 diff 驗)。
- [S3b]:pin_noise 在同一 fixture 下新舊尺數字相同(語意不隨 condensed 動)。
- [S3c]:--ablation 在 condensed 模式不再 rc3(原 fixture 翻綠),coverage 低時輸出弱證據標記。
- 真機驗收:下一次週考卷 log 出現新尺行+coverage 行;08-22 那個「補去尾 s 未標 4→9」的消融案例在 condensed 下重跑,分數不再因未標增加而下降(方向斷言)。

## 實務隱患

- **守衛面**:評測 gate 是排序調參的守門,改尺=改守門標準——故走完整設計審+代碼審;雙報過渡期保留舊尺可對照,發現新尺失真可即時回退(metric_rev 切回)。
- **相容性**:history 舊列凍結不重算;metric_rev 缺欄=舊尺列,讀側以缺欄判版。已排除:不碰金流/對外送出/不可逆操作(評測純本機唯讀計算+新增欄)。
- **condensed 已知偏差**:愛撈未標的系統被高估——[S2] coverage 門檻+補標管線([S4])對沖;門檻首輪實測後定,暫用 0.5 需在實作驗證紀錄回頭校準。
