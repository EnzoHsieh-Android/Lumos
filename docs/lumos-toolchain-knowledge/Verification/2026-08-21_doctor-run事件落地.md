---
type: verification
status: pass
date: 2026-08-21
valid_under: "run_doctor 的 --ci 落帳點未重構;cmd_gov 預設畫面與 --stats 共用 ded 的結構未變"
revalidate_when: "改 _append_governance_log/cmd_gov 去噪;新增會寫治理帳的 gate;棘輪案立案時(本事件是其分母)"
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/doctor-run事件_計劃]]"
---
# 2026-08-21_doctor-run事件落地

> 白話:巡檢 `--ci` 現在每次固定留一筆「我跑過了」,乾淨的 run 不再是帳本上的空白。順手修掉一個兩個月的老問題:vault 範本的 `.gitignore` 放錯一層,從來沒忽略到任何帳檔。

## 驗證

- **TDD 先紅後綠**:`t_doctor_ci_writes_run_marker`(5 斷言)+`t_gov_hides_run_marker_unless_full`(4 斷言,含「尾端筆數==實際印出」與「--stats 去重筆數==2 斷數字」)+ scaffold 測試加 6 斷言(`docs/.gitignore` 同層、真的被 `git check-ignore` 忽略、vault 內不再放無效檔)。全量 **2901 passed / 0 failed**。
- 真跑:`doctor --ci` 後 `gov --stats` 出現 `doctor-run` 列;`gov` 預設畫面不印;`--full` 印。
- `_KNOWN_GATES` 加 `doctor-run`(漂移測試自動釘)。

## 設計審查史(如實)

light r1 blocker→ratchet 升 standard;std r1 major×1;r2 minor×2;r3 s2 一條 major(尾端筆數含隱藏列;★其引句格式不合格形式不採信,編排者自核成立折入★)。K=2 下形式上**未收斂**,2026-08-21 Enzo「順便修掉」=人裁放行+附帶修 gitignore。四輪每輪都抓到一條真的(欄位名/隱藏機制/過濾位置/尾端計數),全部有測試釘。

## 附帶修正:帳檔 .gitignore 放錯層(根因)

`_scaffold_project` 自 2026-06-26 把帳檔 ignore 清單寫在 `docs/<slug>-knowledge/.gitignore`,但帳檔全部落在 `docs/`(`vault.parent`)——**上一層,從來沒生效**。本 repo 五本帳因此全被追蹤(3MB),筆記「皆 gitignore」長期為假(L4 清帳 2026-08-21 才更正)。現改寫到 `docs/.gitignore` 並補 `.usage-log`/`.ci-log`。★既有 repo 已追蹤的帳檔不受影響(gitignore 不 untrack)——本 repo 刻意維持追蹤:帳檔現在是 gov --stats/未來棘輪的資料地基,要不要 untrack 是另一個決定,未動★。
