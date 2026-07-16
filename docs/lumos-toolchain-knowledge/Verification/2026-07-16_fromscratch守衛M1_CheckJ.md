---
type: verification
status: pass
created: 2026-07-16
updated: 2026-07-16
plan_refs:
  - "[[Projects/from-scratch重生守衛_計劃]]"
related:
  - "[[Systems/lumos-cli-read]]"
  - "[[Systems/lumos-cli-write]]"
valid_under: "scripts/lumos 單檔 CLI;check_regen_provenance 共用檢查器架構;INV_TAG_RE=test|audit|kill|src|git 五族"
revalidate_when: "cmd_lint/run_doctor 檢查架構重構、INV_TAG_RE 家族增減、_refcheck_scan 抽取規則變更時"
summary: |-
  TEST:24/24 綠(t_check_j_regen 21 格+t_check_j_git 3 格,含 shallow clone --no-local --depth=1 真實測);全套 1154 綠;真實 vault doctor 0 issues(122 篇,無 regen 節點=Check J 靜默)
  VERIFY:M1 Check J(regen 重生來源守衛)落地——J-a 拒發明合約(regen 節點的 INVARIANT 標記行需 [src:]/[git:] 意圖證據,與 Check T [test:] 疊加)/J-b DECISION 四態(證據/推測/佚失/裸→擋)/J-c substring gate(_validate_repo_ref 直驗不經 top_dirs 靜默過濾+git cat-file+shallow 降 warn 顯性)/J-d 唯讀計數提醒
  KEY:共用 check_regen_provenance(note,repo_root)->(errs,warns,gov_events)——lint 與 doctor 同函式防漂移;映射表:errs→lint rc1/doctor warn(hard),warns→lint 顯示不計 rc/doctor warn_soft,gov_events→僅 doctor --ci 落帳(lint 高頻不落帳)
  KEY:雙報消歧 predicate 落地——regen 節點「推測前綴+INVARIANT 標記」同行時恰一則 J 專屬訊息(generic 位置錯誤 continue 跳過);非 regen 節點 generic 兜底保留(該形態對 INVARIANT_RE 隱形的毒由兜底接)
  KEY:touchpoints——SCALAR_KEYS+regen/INV_TAG_RE 擴 src|git(11 處呼叫點,contracts 顯示驗乾淨)/_refcheck_scan 重構走共用 _validate_repo_ref(既有 refcheck 測試無迴歸)/SRC_REF_RE+GIT_REF_RE+REGEN_PREFIX_RE 新正則
---
# 2026-07-16 fromscratch守衛 M1 Check J 落地驗證

[[Projects/from-scratch重生守衛_計劃]] M1 的實作驗證。design-loop 3 輪 panel 人裁實質收斂（golden: `governance/golden/fromscratch-m1/`）後照 spec v4 落地。

## 驗證項

- **t_check_j_regen（21 格）**：set regen 白名單迴歸 rc0、非 regen 節點不受影響、J-a 兩態、J-b 四態、J-c 假頂層目錄/越界/合法（top_dirs 靜默放行迴歸測）、raw 行四組合（推測/佚失 × INVARIANT/IRREVERSIBLE）皆 rc1 專屬訊息、INVARIANT 組合恰一則（消歧 predicate）、非 regen generic 兜底、J-d 提醒不擋、contracts 顯示剝 [src:]、doctor 兩入口（違規 --ci rc1 / 合規 rc0 + warn_soft 不計 issues）。
- **t_check_j_git（3 格）**：真 sha rc0、假 sha dangling rc1、shallow clone（`--no-local --depth=1` 真建）缺物件 → rc0 + 「Tier B 驗證跳過」顯性標示。
- 全套 1154 綠（含既有 refcheck 測試——`_validate_repo_ref` 抽取重構無迴歸）；真實 vault doctor 0 issues。

## 誠實邊界

- 宣告制：不標 `regen` 完全繞過 Check J（opt-in 結構性限制，spec 已載）；J-c 只驗「指針可解析」不驗「內容真支持 claim」（語意層留 M2 對抗審）。
- gov_events 落帳僅驗「doctor --ci 通道接上」（既有 `_append_governance_log` 機制未另測 e2e 帳檔內容）。
