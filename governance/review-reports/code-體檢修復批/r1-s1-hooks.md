# r1-s1 對抗審計 — Gate L (pre-commit lint) + code-ext 四份清單

審查方式:非憑讀碼推論,對每個提問在乾淨臨時 git repo 跑「真的 hook」驗證(場景見下)。Diff:
`governance/review-reports/code-體檢修復批/r1-diff.patch`(9a95bc4..HEAD, scripts/ + governance/autonomous-loop.sh)。

## Blocker

無。

## Major

### M1 — Gate L 用檔名 stem 找節點,不是用真正 staged 的路徑;檔名撞名時會「lint 錯節點」並靜默放行壞節點

- `scripts/hooks/pre-commit:93` 呼叫 `"$CC_PY" "$REPO_ROOT/scripts/lumos" lint "$f"`,`$f` 來自
  `git diff --cached --name-only`,是**repo-root 相對路徑**(如
  `docs/x-knowledge/Systems/dup.md`)。
- `lumos lint` 內部 vault 是 `find_vault(Path.cwd())`(`scripts/lumos:14845`,cwd=REPO_ROOT),
  `env.notes` 的 key 是**vault 相對路徑**(如 `Systems/dup.md`,不含 `docs/x-knowledge/` 前綴)。
- `Env.find()`(`scripts/lumos:293-303`)第一步是精確路徑比對
  `if "/" in a and (a + ".md") in self.notes`(L298)——但傳進來的 `a` 永遠帶著
  `docs/x-knowledge/` 前綴,不可能等於任何 vault-相對 key,**這條分支對 Gate L 的呼叫方式恆假**。
  於是每一次 Gate L 的 lint 呼叫,實際上都落到 L300 的
  `self.by_stem.get(a.rsplit("/", 1)[-1].lower())`——純檔名 stem 查找,完全不看資料夾。
- 後果:vault 裡只要有**兩個節點同檔名(不同資料夾)**,`by_stem` 命中多筆時只取第一筆
  (`scripts/lumos:301-303`,只印一句 stderr 警告、不影響 rc),Gate L 可能對著「另一個已經
  乾淨、已 commit 過的同名節點」跑 lint,而完全沒碰到真正 staged、壞掉的那個節點——lint 回報
  0 問題,rc=0,壞節點直接放行進 commit。這正是 Gate L 存在的目的(「lint 從未被任何 hook 呼叫」)
  要防的那類漏洞,現在换了個形式又漏回來。

**重現(在乾淨臨時 repo,真的跑 `scripts/hooks/pre-commit`)**:

```
mkdir -p docs/x-knowledge/{Systems,Issues} && git init -q
# 先 commit 一個乾淨節點 Issues/dup.md
cat > docs/x-knowledge/Issues/dup.md <<'EOF'
---
type: issue
status: open
summary: |-
  KEY:baseline good node
---
# dup (Issues, 已 commit,乾淨)
EOF
git add -A && git commit -q -m baseline

# 再 stage 一個「同檔名、不同資料夾」的壞節點 Systems/dup.md(缺 summary block,system 型別必錯)
cat > docs/x-knowledge/Systems/dup.md <<'EOF'
---
type: system
status: doing
---
# dup (Systems, NEW, staged, 壞:system 型別缺 summary block)
EOF
git add -A
bash scripts/hooks/pre-commit; echo "rc=$?"
```

實測輸出:`rc=0`(**放行**)。對照直接單獨跑同一份 lint 邏輯(用 vault 相對路徑,不經 Gate L 的
repo-root 路徑轉換問題):

```
$ python3 scripts/lumos lint "docs/x-knowledge/Systems/dup.md"
⚠ 同名筆記 2 個,取第一個: Issues/dup.md
✓ lint Issues/dup.md — 0 問題      ← lint 錯的節點,靜默放行

$ python3 scripts/lumos lint "Systems/dup.md"     # 用真正 vault 相對路徑
lint Systems/dup.md
  ✗ system 節點必須有 summary block(放 FLOW:/KEY:/DEP: 等符號行)
1 error / 0 warning                ← 這才是應該擋下的結果
```

這不是罕見角落:在一個以「主題」命名節點的圖譜裡,同一主題先開 Issue 後升格 System、或不同
Verification/Project 節點意外重名,都是可預期的真實情境。且錯誤是**完全靜默**的——pre-commit
只在 `out="$(...)"` 對應指令 rc≠0 時才印出 `$out`(L93-95),這裡 rc=0,連「⚠ 同名筆記」的
stderr 警告都被吞掉(該警告寫進 `out` 變數但從未被印出)。新增的
`t_precommit_lints_staged_graph_nodes` 測試(`scripts/test_lumos.py`)只測「vault 裡恰一個
節點」的情境,不會發現此洞。

**建議修法**:Gate L 呼叫 lint 時應該用「相對於 vault 的路徑」,或讓 `Env.find()`
在收到帶 vault 前綴的路徑時也能精確比對(例如剝掉 `$GRAPH_ROOT/` 前綴後再查),不要仰賴
stem fallback 作為主要解析路徑。

## Minor

### N1 — Gate L 在 python/lumos 缺席時「完全靜默」跳過,不像 Gate CC 有提示

`scripts/hooks/pre-commit:88` 的判斷式與 Gate CC(L38)相同(`CC_PY` 非空 + `scripts/lumos`
存在),但 Gate CC 在條件不成立時會印
`"pre-commit: 無 python3 或 scripts/lumos,跳過 co-change 警告"`(L45),Gate L 沒有對應訊息
——條件不成立時整段 if 直接跳過,沒有任何 stderr 留痕。實測(PATH 裡拿掉 python3、保留
`scripts/lumos`):只看到 Gate CC 的訊息,Gate L 全靜默。屬 fail-open 設計內的行為(不會誤擋
commit),但「硬擋閘位默默失效卻無訊號」在一個以「留痕」為核心紀律的專案裡值得補一句
echo,否則某台缺 python 的機器可能長期繞過 Gate L 而沒人發現。

### N2 — Gate L 每個 staged 節點各起一個 Python 行程重載整個 vault,commit 延遲隨 staged 節點數線性增長

實測(乾淨臨時小 vault,30 個 staged 節點全乾淨):`bash scripts/hooks/pre-commit` 耗時
**5.25s**(≈175ms/節點)。用本 repo 真實 vault(316 篇 `docs/lumos-toolchain-knowledge`)量測
單次 `lumos lint <file>`:**0.21s**(每次呼叫都重新 `load_vault` 全圖 + 起一個新 Python
行程)。所以一次改動 30 篇圖譜節點的大重構,pre-commit 會多花 ~6s。不影響正確性,純屬
「每檔 <1s」的設計假設(pre-commit L87 註解)在多檔情境下線性疊加成有感延遲,值得注意但不到
擋 major 的門檻。

## 已驗證「不是問題」的項目(逐項回覆 LENS 提問)

- **staged .md 被刪除**:`[[ -f "$f" ]] || continue`(pre-commit L92)正確跳過,實測 rc=0,無誤判。
- **rename(R status)**:`git diff --cached --name-only` 對 rename 只吐新路徑(`R100 old new`
  在 `--name-status` 下才看得到兩欄,`--name-only` 只給新檔),Gate L 對新檔名跑 lint,實測正常
  放行/擋下如預期。
- **CJK / 含空白路徑**:實測 `docs/x-knowledge/Systems/中文 節點 名.md`,`core.quotePath=off`
  正確避免加引號,Gate L 正確定位、正確擋下缺 summary 的壞節點,修好後正確放行。
- **`scripts/lumos` vendored 但 python 缺席**:實測拿掉 PATH 裡的 python3/python,Gate L 判斷式
  為假、整段跳過(fail-open,不誤擋),但參見 Minor N1(靜默無提示)。
- **consumer repo 圖譜根目錄不同**:實測 `docs/myproj-knowledge/`(`docs/*-knowledge` 型)與
  `docs/knowledge/`(fallback 型)兩種都正確被 GRAPH_ROOT 偵測到,Gate L 正常運作(仍受 M1
  影響,但與圖譜根目錄命名本身無關)。
- **Gate 1 / Gate 2 順序,「docs-only → 放行」是否在 Gate L 之後**:讀碼 + 實測皆確認 Gate L
  (`pre-commit:88-102`)位於「無 code 檔案 → 放行」的 Gate 2(`pre-commit:126`)之前。這代表
  **行為確實改變**:以前一個純圖譜、無 code 異動的 commit,不管節點寫得多爛都直接放行(Gate 2
  的「沒 code → exit 0」是唯一擋點);現在 Gate L 先攔一手,壞的圖譜節點就算不帶任何 code 異動
  也會被擋。這是 spec #6 明確要的效果(「lint 從未被任何 hook 呼叫」),經 CJK 案例實測確認
  按預期運作,**非缺陷,是本 diff 的核心行為變更**,提醒使用者這確實會擋下一些以前能過的
  docs-only commit。
- **`lumos lint` 是否會對非硬性 warning 回傳 rc≠0**:讀碼確認 `cmd_lint`
  (`scripts/lumos:2606-2798`)最終 `return 1 if errs else 0`(L2798),`warns` 清單
  (SYMBOL 行 typo、`feature/area` 標籤家族凍結提示、★CHECKPOINT★ 缺回退建議等)全部**不影響
  rc**——只有 `errs`(缺 type/summary、裸 ★INVARIANT★、decisions 結構壞損、status/tags 漂移等)
  才會讓 rc=1。故 Gate L 不會因為既有「只是 warning」的舊毛病而讓以前能過的 commit 突然被擋。
- **post-commit / pre-commit 正則是否誤判 `.shx` 或 `foo.sh.bak`**:實測 staged
  `src/weird.shx`、`src/backup.sh.bak`、`src/real.sh` 三檔,pre-commit Gate 2 僅把 `real.sh`
  判定為 code(訊息明列 `Staged code files (1): • src/real.sh`),`.shx`/`.sh.bak` 皆未誤判;
  `--no-verify` 提交後 post-commit 的 bypass 留痕同樣只算 1 個 code 檔。原因:bash 正則
  `\.(...|sh|ps1)$` 有 `$` 錨定在字串尾端,`.shx`/`.sh.bak` 的尾碼不是 `sh`/`ps1`;Python 側
  `check-graph-sync.py`/`impact-hook.py` 用 `Path.suffix.lower() not in CODE_EXTS`
  是精確字串比對(`.shx`≠`.sh`),同樣不會誤判。另外用腳本直接抽取四份清單比對,`pre-commit`/
  `post-commit`/`check-graph-sync.py`/`impact-hook.py` 的副檔名集合逐字相同(含新加的
  `.sh`/`.ps1`),`t_code_exts_four_lists_agree` 測試如實反映現況。

## 附:實際跑過的新測試(確認宣稱與現況一致)

`t_precommit_lints_staged_graph_nodes` / `t_code_exts_four_lists_agree` /
`t_merge_dedupes_preexisting_duplicates` 三條單獨執行皆綠;但如 M1 所述,這些測試的覆蓋範圍
沒有涵蓋「vault 內檔名撞名」情境,是本次揪出 M1 的關鍵缺口。

---

嚴重度統計:blocker=0, major=1, minor=2
