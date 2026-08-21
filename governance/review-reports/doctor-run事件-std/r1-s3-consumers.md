# doctor-run事件-std r1-s3 對抗審計 — LENS: existing consumers / CI / hooks

角色:獨立第三方審計,對抗但憑事實。對象=`/tmp/doctor-run事件-std-r1.md`(spec,尚未落地——`scripts/lumos`/`scripts/test_lumos.py` 均無 `doctor-run` 字樣)。範圍鎖定 dr-common 指定的四問:CI 是否會因帳本恆變而翻紅、pre-push 到底跑哪個 doctor、code-loop 簿記豁免是否含這個檔、以及**這件事在被 vendor 出去的消費專案身上會不會放大**。

白話結論先講:這份設計不會讓任何測試或 CI 變紅,機制本身自洽;但它會讓「每次 `git push` 完本機工作樹就髒一行」這件事,從「偶爾發生」變成「源 repo + 每一個裝了 lumos 的消費專案,永遠都會發生」——而且我實測發現,消費專案 scaffold 出來的 `.gitignore` 根本沒蓋到這個檔案(放錯層,一直是無效的忽略規則),帳本因此是真的進 git 版控、真的在長(源 repo 現在這個檔已經 3MB)。這不是這份 spec 造成的舊洞,但 spec 把寫入頻率從「偶爾」改成「每次」,會讓這個舊洞在每個消費專案裡都被踩得更頻繁。

## 逐問核對(dr-common 四問)

### Q1:CI 是否在 `doctor --ci` 後檢查工作樹乾淨(`git diff --exit-code`/porcelain)?

`.github/workflows/ci.yml` 完整內容已讀過:`Compile check` → `SyntaxWarning 歸零閘` → `Full test suite` → `Graph doctor (strict)`(`python scripts/lumos doctor --ci`)→ `Anchor verify`。**沒有任何一步做 `git status --porcelain`/`git diff --exit-code`/commit 帳本比對**。CI runner 是 ephemeral checkout,`doctor --ci` 寫的那行不會被推回 repo。**結論:不會翻紅,無風險。**(與 r1-s1 的核對一致,獨立複查通過)

### Q2:pre-push 到底跑 `doctor` 還是 `doctor --ci`?

`scripts/hooks/pre-push:148`:
```
if "$PY" "$GRAPHCTL" doctor --ci; then
```
**是 `--ci`,不是純 `doctor`。** 這代表本機每次 `git push`(只要 repo 裡有 vault)都會走到 `_append_governance_log` 分支——這件事在此 spec 落地後,從「只有偵測到新問題才寫」變成「不管乾不乾淨都寫一行」。這是 Q4 放大效應的根源,見下。

### Q3:`docs/.governance-log.jsonl` 是否在 `_BOOKKEEPING_FILES`,讓恆變的帳本不會廢掉 code-loop pass/skip 留痕?

`scripts/lumos:10299-10300`:
```python
_BOOKKEEPING_FILES = ("docs/.governance-log.jsonl", "docs/.usage-log.jsonl",
                      "docs/.ci-log.jsonl", "governance/anchor-baseline.json")
```
已經在裡面,不需要為本案新增。豁免判定式在 `scripts/lumos:14113-14126`(比對 `rec_sha` 到 `marker_sha` 之間的 commit 是否**全部**落在白名單內,是則留痕仍算數)。有專屬回歸測試 `t_codeloop_pass_survives_bookkeeping_commits`(`scripts/test_lumos.py:8214-8244`),測試自己的注解就寫「pass 自己會往★tracked★的 docs/.governance-log.jsonl append 一行」,證明「這個帳本是 git 版控追蹤的檔案」是團隊已知、已修過一次事故(`Issues/code-loop-pass自失效追尾`)的既有事實。**結論:無缺口,本案不需要動這裡。**

### Q4:vendor 出去的消費專案——會不會也跑 `doctor --ci`?帳本會不會一樣長?`scripts/templates/` 有沒有 gitignore 保護?

**會跑,而且是逐檔複製同一套機制,不是重寫過的輕量版:**
- `_vendor_toolchain`(`scripts/lumos:8826`)呼叫 `_scaffold_project(root, slug)` + `_install_hooks_py(root)`,然後對 `scripts/hooks`、`scripts/templates` 兩個目錄 `rglob("*")` 逐檔比對複製(`scripts/lumos:8845-8848`)。`scripts/hooks/pre-push` 整檔被複製過去,Q2 的 `doctor --ci` 呼叫是**逐字相同**的檔案,不是消費端重寫的簡化版。
- `install-graph-toolchain.sh` 只是薄殼,直接 `exec python3 lumos init`(`scripts/install-graph-toolchain.sh:16-20`),走的是同一條 `_vendor_toolchain` 路徑。
- `scripts/templates/` 目前只有 `graph-discipline.md` 一個檔,**沒有任何 `.gitignore` 範本**——消費端的忽略規則完全不是從這裡來的。

**忽略規則實際從哪裡來、有沒有蓋到:** `_scaffold_project`(`scripts/lumos:8958-8969`)在**vault 目錄本身**(`kg = root/docs/{slug}-knowledge`)寫入:
```python
_write_lf(kg / ".gitignore",
          ".bypass-log.jsonl\n.rot-queue.jsonl\n.governance-log.jsonl\n.canary-log.jsonl\n.kill-log.jsonl\n.signoff-log.jsonl\n")
```
但所有這些帳本的實際寫入點清一色是 `vault.parent`(`docs/`),**比 vault 高一層**——`_append_governance_log` 的 `path = vault.parent / ".governance-log.jsonl"`(`scripts/lumos:437`),signoff 在 `scripts/lumos:2871`,canary 在 `scripts/lumos:3358` 等多處,kill 在 `scripts/lumos:5689`,usage 在 `scripts/lumos:6047`——**都在 `docs/.xxx-log.jsonl`,不在 `docs/<slug>-knowledge/.xxx-log.jsonl`**。Git 的 `.gitignore` 規則只對自己所在目錄「以下」生效,不會反向蓋到上一層。這個 scaffold 出來的忽略規則因此結構性地永遠蓋不到它列的那些檔案。

我在**本 repo自己身上**實測驗證這個落差是真的、不是我推論錯:
```
$ git check-ignore -v docs/.governance-log.jsonl
(無輸出,exit 1 = 沒被忽略)
$ git ls-files docs/.governance-log.jsonl
docs/.governance-log.jsonl              ← 確實被追蹤
$ ls -la docs/.governance-log.jsonl
-rw-r--r--  1 enzo  staff  3011970 ...   ← 目前 3.01 MB
```
`docs/.bypass-log.jsonl`(16KB)、`docs/.canary-log.jsonl`(287KB)、`docs/.signoff-log.jsonl`(2.9KB)、`docs/.usage-log.jsonl`(15.5KB)同樣全部被追蹤;唯一真的被忽略的是 `docs/.ci-log.jsonl`,但那是**根目錄** `.gitignore`(`.gitignore:8`)裡單獨明列的路徑,跟 vault 內那份完全是兩套規則、互不相干。

**這是不是 bug、還是刻意設計?** 兩者證據都有——`scripts/lumos:9405` 附近有「(帳在 git 版控下,diff 定位一分鐘可修…)」這種明確承認 canary-log 是**故意**版控的註解,`t_codeloop_pass_survives_bookkeeping_commits` 的測試敘述也直接寫「★tracked★」。所以「這些帳本進 git」本身看起來是團隊已知且承認的設計,vault 內那份 `.gitignore` 更像是放錯位置的殘留/未清乾淨,而非本案要修的東西——**我不把它算進本案的缺陷,但它是理解 Q4 影響半徑的必要事實**。

**跟本案的交集在哪:** 這個「帳本進版控」的既有事實,本來只在「有 issue/有 gov 事件」時才會被 touch——對消費專案來說是低頻的。本案把寫入頻率改成「不管乾不乾淨、每次 `--ci` 都寫」,而 Q2 已確認每個消費專案的 pre-push 都跑 `--ci`。兩件事疊起來,結果是:**每一個裝了 lumos 的消費專案,從今以後每次 `git push` 都會讓一個被 git 追蹤的檔案多一行、工作樹立刻變髒**,而目前完全沒有自動 commit 這行的機制(`grep` 過 pre-push/lumos 找不到任何自動 `git add`/`git commit` 這個檔的邏輯)。

## 嚴重度判定

這個放大效應**不會讓任何機制真的失效**——已核對 Q1(CI 不查乾淨度)、Q3(code-loop 簿記豁免逐字同步 vendor 到消費專案,一樣接得住)。r1-s1、r1-s2 兩席已經在「源 repo 單一視角」下把同一現象判為 minor,理由正是這套豁免機制本來就吸收得住、不構成功能性破壞。我在此獨立核對後同意這個判斷、且把範圍擴大確認到「消費專案全體」也一樣被同一套機制接住——**不升級為 major**。

但這件事在「消費者」視角上有兩點值得記進節點、目前設計文件完全沒提到:
1. 影響半徑是「每一個消費專案」而非單一 repo——spec 的「範圍刀」「實務隱患」兩段只講源 repo 層級的效能/風險,沒有意識到 pre-push + scaffold 是逐檔 vendor 出去的,消費端承受的是同一份放大效應,乘以專案數。
2. 現有 3MB 的 `docs/.governance-log.jsonl` 是在「只在有事件時寫」的舊行為下長出來的;改成「每次都寫」後,寫入頻率的量級變化(從「issue 觸發」到「每次 push/CI 都觸發」)沒有在文件裡被量化或討論過,只寫了一句「效能——每次 --ci 多一行」,把這個成本講得比實際更小。

引句:「乾淨 run 因此恆有一筆可寫」(`/tmp/doctor-run事件-std-r1.md` 設計節)——此句本身核實為真(已與 `_append_governance_log`/`pre-push:148` 對照),但文件通篇沒有一處把這句話的後果(消費專案 fleet-wide 帳本恆髒 + 加速版控成長)寫進風險評估。

severity: minor(機制不破,已有豁免通道全數承接;但影響範圍與量級被文件低估,建議設計節或範圍刀段落補一句,並列為棘輪案 [[Projects/檢核收緊五件_計劃]] 的後續觀察項)。

## Q5(dr-common 額外指定):`t_gov_stats_gate_drift` 對新寫入點的字面值要求

`scripts/test_lumos.py:3047-3062` 有兩條釘子:①全檔 `"gate": "字面值"` 必須 ⊆ `_KNOWN_GATES`;②`"gate": ` 後面**不是**字串字面值的位置必須恰好 1 處(目前唯一合法動態寫點是讀側 passthrough `scripts/lumos:2994` 的 `"gate": d.get("gate", "?")`)。

spec 設計節給的寫法是 `{"gate": "doctor-run", "kind": "ran", ...}`——**是字面值**,不會增加動態寫點計數(仍維持 1 處),只要同步把 `"doctor-run"` 加進 `_KNOWN_GATES`(spec 已明確列為待辦),兩條釘子都過。**核實通過,無缺口。**(與 r1-s1 獨立核對結果一致)

## 結論

四問(+Q5)全數核對完畢,對照真代碼(`scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`、`scripts/test_lumos.py`)逐行印證,本輪(consumers/CI/hooks 視角)未發現 blocker 或 major——CI 不會翻紅、pre-push 確認跑 `--ci`、code-loop 簿記豁免確認涵蓋且逐字 vendor 到消費專案、`t_gov_stats_gate_drift` 字面值要求確認滿足。發現一條 minor:設計文件低估了「帳本恆變」在消費專案 fleet 上的影響半徑與量級,建議補述但不構成放行障礙。

findings: blocker=0 major=0 minor=1
