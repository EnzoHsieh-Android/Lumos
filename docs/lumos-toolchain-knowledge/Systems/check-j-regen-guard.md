---
type: system
status: done
created: 2026-07-16
updated: 2026-07-16
self_audit: sonnet/2026-07-16
tags:
  - type/system
  - status/done
related:
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/lumos-refcheck]]"
  - "[[Systems/外部對照-code衍生wiki]]"
plan_refs:
  - "[[Projects/from-scratch重生守衛_計劃]]"
verified_by:
  - "[[Verification/2026-07-16_fromscratch守衛M1_CheckJ]]"
summary: |-
  FLOW:重建節點 → lumos set regen from-scratch/日期 蓋章 → summary 逐 claim 標身分([src:]/[git:]/推測:/佚失:) → lint/doctor 共用 check_regen_provenance 執法 → 查證後補證據或 signoff 升級
  KEY:解 from-scratch 重生塌陷——重建=從 code 快照逆向工程 why,AI 會編自信假 why/假合約;Check J 逼每條 claim 亮身分:有證據(且機械驗真)/推測/佚失 三選一,把「不知道」留成「不知道」(anti code-衍生wiki 原罪,見 [[Systems/外部對照-code衍生wiki]])
  KEY:J-a 拒發明合約(regen 節點 INVARIANT 標記行需 [src:]/[git:] 意圖證據,與 Check T [test:] 疊加——test 證行為,src/git 證意圖)｜J-b DECISION 四態(證據/推測/佚失/裸→擋)｜J-c substring gate(_validate_repo_ref 直驗+token 消毒:空/絕對/.. traversal 皆 missing;git cat-file;shallow 降 warn 顯性+僅 --ci 落帳)｜J-d 無標記 KEY 行唯讀提醒
  KEY:共用 check_regen_provenance(note,repo_root)->(errs,warns,gov_events),lint 與 doctor 同函式防兩入口漂移;映射:errs→lint rc1/doctor warn(hard),warns→兩入口皆非阻擋,gov_events→僅 doctor --ci;雙報消歧 predicate=regen 節點推測+INVARIANT 同行恰一則 J 訊息、非 regen generic 兜底
  KEY:★DEBT★ 宣告制 opt-in——不蓋 regen 章完全繞過 Check J,且繞過無留痕、無 Check H 式軟提醒對應;「疑似重生未標」自動偵測留未來
  KEY:天花板——J-c 只驗指針可解析,不驗內容真支持 claim(語意層留 M2 對抗審/人);佚失的 why 永久佚失,正確輸出是佚失標記非編造
  DEP:[[Systems/lumos-refcheck]]｜[[Systems/check-t-sentinel]]
  TEST:27 格綠(t_check_j_regen 24+t_check_j_git 3,含 shallow clone 真實測+token 消毒迴歸);全套 1157
  VERIFY:[[Verification/2026-07-16_fromscratch守衛M1_CheckJ]]
---
# check-j-regen-guard

Check J：from-scratch 重建節點的 provenance 分級守衛。設計三輪對抗審與收斂史見 [[Projects/from-scratch重生守衛_計劃]] 與 `governance/golden/fromscratch-m1/`；使用紀律見 lumos-project-notes skill〈重生標記〉段與 reference〈重生守衛〉段。

## 一句話

重建的筆記每條 claim 被逼亮身分——「有證據（機械驗真）」「推測」「佚失」三選一；想混一句自信的鬼話（尤其假合約），機器擋。

## 教訓（實作級）

- code-review blocker：`_validate_repo_ref` 初版無 token 消毒，`[src: ]`/絕對路徑/`..` traversal 經 pathlib join 語意全判 ok——**拆掉 top_dirs 過濾時要顯式補回它隱含的安全性**。design-loop 3 輪審 spec 語意抓不到 pathlib join 語意：實作級洞要靠實作級審。
