# 架構對齊審查報告——node-restore-sop-v2 r1(v4 delta)

## 問題一:世界解折入有無第二種做法

### finding 1(major)`lumos search --code` 語意挪用
引句:「機器逐篇掃「筆記引用的檔名/函式/欄位是否真的存在於 code」(refcheck/`lumos search --code` 既有零件)」
repo 兩處記載的既有用途(SKILL.md:66、reference.md:1097)一致=「code 拿掉/改名後,查筆記還講不講那個名字」——方向是 code 變→核筆記,不是核「筆記引用的東西在 code 存不存在」;CLI docstring(scripts/lumos:1674)印證它搜的是筆記全文(--code 只是把筆記內 code 區塊納入搜尋),從不碰目標 repo 檔案系統。refcheck 那半是正確複用;search --code 塞進「既有零件」=語意挪用。

### finding 2(minor)refcheck 涵蓋被誇大
refcheck 自己的節點(Systems/lumos-refcheck.md:19)誠實聲明只收 inline-code 的 path[:line] 宣稱——「檔名」答得到,「函式/欄位」答不到。

### finding 3(⚠)動態差分零依賴邊界不明
repo 無任何執行軌跡/覆蓋率機械(testmap=靜態推斷 scripts/lumos:12716;mutate=變異測試 :10425);既有先例排除引 mutmut/cosmic-ray(驗證層去模型化_計劃:86)。但步驟 1④ 講的是目標專案該用自己棧內工具(pytest-cov/JaCoCo/Istanbul),不必然踩 lumos 零依賴家規——spec 沒把「這是目標專案的事,不是 lumos 的事」寫清楚。⚠ 交編排者。

### finding 4(minor)reflexion 與既有機制的關係只在隱患段交代
關係=疊加(MOC 骨架是 stale/self_audit 都管不到的節點型:Check S 只認 type=system、stale 認 valid_under,MOC 兩邊不落),非平行第二套;但步驟 0 引入處看不到這層,要翻到隱患段才拼得起來。

## 問題二:d6 使用場景節

### finding 5(major)三分岔兩處重複、未定單一來源
引句:「有→照既有慣例用;有但殘缺→照步驟 4 前置 diff 補;沒有→走七步產一篇」(:103)
引句:「進場判斷→`lumos search/context`(有→照慣例用;殘缺→diff 補;沒有→往下)」(:146)
三分岔本身是既有「圖譜先行」的本場景特化,對齊;但落地後同時活在 reference.md 大節與 09 查表、字句幾乎相同、無「以另一處為準」——本文自己用整段記錄過「八類」同句五處漂移的失效模式,又在自己身上開新的兩處重複。判 major。

## 問題三:命名與格式

### finding 6(minor)「(世界解:…)」行內標記全庫無先例
掃描 343 篇扣本篇,0 命中;既有 PRIOR-ART 慣例=集中一段講完(openwiki 節點、決策 context 三段式);本篇 PRIOR-ART 大節自己也守了慣例,問題只在步驟本文散布 7 個行內標籤。

### finding 7(minor)d5–d7 content 自帶「dN(…):」前綴無先例
全圖譜 171 條 decisions content 只有本篇 d5/d6/d7 這樣寫;同篇 d1–d4 都不帶。有真實技術理由(decisions 輸出不印 id,scripts/lumos:6443),但屬本輪臨時發明的個案解法,連同篇都不一致。

## 總結
不對齊共 7 條:major 2(search --code 挪用/三分岔未定正本)、minor 4、⚠ 1。
