# 架構對齊審查報告 — 節點還原SOP_計劃 r3 delta

## 一、「d3/d4 文字澄清」KEY 行做法 — major(第二種做法)

目標文 summary 新增「KEY:★d3/d4 文字澄清…決策文字不可改,以本行澄清」(:13),沒有立新 decision。先例兩筆方向一致:①自足性審計閉環_計劃.md:29(d2 why_chosen)逐字「決策文字不可手改,以新決策澄清舊決策」——立新決策澄清舊決策;②驗證層去模型化_計劃.md:40 處理「目標本身是 KEY 行」的更棘手情境,做法也是「decision-add(新決策載明翻案+引原文)+KEY 行同步改寫」雙軌。全庫唯一用「KEY 行單軌澄清」的樣本就是目標文自己。判 major。

## 二、步驟 4 重述重生守衛① — ⚠ 判不準

引句:「舊節點還在(哪怕殘缺)就照重生守衛第一條 **diff 更新、別整篇換**(保住殘存目擊內容」(:98)
與 reference.md:630 原文逐字比對:核心語句無走樣(多一頓號+「哪怕殘缺」操作性補充,方向一致)。但同文件步驟 5 明文「實形照 reference.md…本文不重抄防漂移」——兩步驟重抄政策不一致;repo 兩種慣例並存(純指標派:check-j-regen-guard.md:35/精簡重述派:reference.md:649「兩版並存」),且 [S1] 落地後本段就在 reference.md 內部。判不準,標 ⚠。

## 三、考古紅線缺既有慣例 — 非不一致

全庫 grep 敏感/機密/憑證/secret/credential/資安/外洩+.gitignore+hooks+CLAUDE.md:查無任何「考古挖出敏感內容如何處理」既有政策(命中皆無關語境;.gitignore 無 secret 樣式;hooks 無 secret-scan)。目標文自述「無既有政策可繼承」查證屬實,自建新規是正確處置。

## 四、[S3] entry-hook.py 直接改字 vs anchor 慣例 — 非不一致

governance/anchor-baseline.json 錨點只 5 檔(test_lumos/test_autonomous_loop/pre-commit/pre-push/post-commit);Systems/anchor-integrity.md:32(d2)明文「錨點集合 v1 固定列舉 5 檔」,精神=只守驗證器,不含 Claude hooks。entry-hook.py 不在清單,[S3] 不提 anchor approve 是正確的。

## 總結

不對齊共 1 條,其中 major 1 條(d3/d4 澄清應立新決策+KEY 行雙軌,非 KEY 行單軌);另 1 條 ⚠ 不計入。
