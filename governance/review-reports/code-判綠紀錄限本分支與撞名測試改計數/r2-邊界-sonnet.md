severity: major

**審查範圍**:固定版本 6e10ae5b(修前 409ab14f)。逐 hunk 讀完 `r2-snapshot.patch`,另在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/邊界-sonnet/` 下用臨時 repo 實跑。git 為 Apple Git 2.39.2,Python 3.14.6,只在這一台 macOS 上驗。

## Findings

1. 部分複製只認舊式設定,新式部分複製照樣為了判祖先去連遠端,修補要擋的錯沒擋到

引句:「pc = _lens_git_dl(rr, "config", "--get", "extensions.partialClone", deadline=deadline)」

- 位置:`_redbase_on_branch` 裡的 `repo_kind()`。
- 問題:偵測部分複製只看 `extensions.partialClone`。git 官方 partial-clone 文件寫明,promisor remote 由三個設定各自獨立認定:`extensions.partialClone`、`remote.<name>.promisor=true`、`remote.<name>.partialCloneFilter`。
- 本機實測:`git clone --filter=blob:none` 只寫了 `remote.origin.promisor=true` 和 `partialclonefilter=blob:none`,沒有 `extensions.partialClone`。
- 結果:這種部分複製被判成 `full`,整批照問 git。本機沒有的提交會觸發自動連遠端。
- 影響:`merge-base --is-ancestor` 和 `cat-file -e` 各連一次,每個不同的 head_sha 最多 2 次。計劃 S8 與做法 1 d 要擋的就是這件事。
- 測試缺口:`t_redbase_branch_rows_fallback_keeps` 的部分複製夾具只設 `extensions.partialClone`,新式設定從沒被測到。

最小重現(`/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/邊界-sonnet/exp/e3.py`):
1. `git clone --no-local` 一個 repo。
2. 設 `core.repositoryformatversion=1`、`remote.origin.promisor=true`,不設 `extensions.partialClone`。
3. 把 `remote.origin.uploadpack` 換成會 `touch` 記號檔的腳本。
4. 治理帳放一筆 `head_sha="ab"*20` 的判綠紀錄。
5. 呼叫 `_redbase_branch_rows(pc,"甲",None,"ignored")`。

證據表:
- claim:部分複製判定漏掉只靠 `remote.<name>.promisor` 的新式設定
- input:上述 promisor-only 設定加不存在的 sha
- expected:不連遠端,照留並印一句
- case_source:自補案例,不在作者案例表內
- before(409ab14f):舊式、新式兩種設定都連遠端(`remote contacted: True`)
- after(6e10ae5b):舊式設定不連遠端,印「1 筆判不了」。新式設定 `remote contacted: True`,結果是 `[]`(該筆被當成不存在而丟掉)
- 歸因:有證據的原有漏查。修補只修了舊式設定,新式設定修前修後都連遠端,不是修補造成的回歸。
- 限制:真實支援 filter 的伺服器是否另寫 `extensions.partialClone`,我這台沒驗成。本機伺服器回「filtering not recognized」,但 git 仍只寫了 promisor 兩個鍵。

severity: major
blocking: 是

2. S6「同名重開」案例沒有前置斷言,證明不了判綠紀錄真的寫進帳

引句:「check("S6 同名重開、判綠那時的提交不是祖先:照存", "redbase" in rec, (rec.get("redbase_skipped"), out[-500:]))」

- 位置:`t_spec_gate_redbase_green_other_branch` 的 gb3 段。
- 缺口:沒有斷言「判綠紀錄真的寫進帳,而且它的 head_sha 現在不是 HEAD 的祖先」。同一支測試的 S1 段有斷言 ref,S7 測試有 `★前置★`,只有這段沒有。
- 失敗場景:判綠事件沒寫進帳(例如夾具的 `git commit` 被使用者的簽章設定擋掉)時,規格閘本來就會存紅燈版。`"redbase" in rec` 照綠,過濾判斷根本沒被走到。
- 違反:`Systems/測試假綠形態` 的 ★INVARIANT★,即還原翻紅釘必須配前置斷言證明現場成立。
- 補充:實際跑 12 條斷言都過,且作者案例表說改壞 G2 會紅。所以這裡是前置缺口,不是目前已經假綠。

證據表:
- claim:S6 同名重開案例缺前置
- input:gb3 流程中判綠事件沒寫入
- expected:測試應先確認現場成立,否則紅
- case_source:本席自補
- before:409ab14f 同一段也沒有前置斷言
- after:6e10ae5b 同一段也沒有前置斷言
- 歸因:未判定。修前修後相同,我沒跑「判綠沒寫入」的改壞,所以不能判是新造成或舊漏。

severity: minor
blocking: 否

## 已驗正向主張

- **同名 tag**:`symbolic-ref --short -q HEAD` 在有同名 tag 時回 `heads/featA`,新的 `symbolic-ref -q HEAD` 去掉 `refs/heads/` 後回 `featA`。修前修後行為相反,G3 修復有效(本機 git 2.39.2,另一版本未驗)。
- **淺複製**:真祖先被截斷、`merge-base` 回 rc 1 時,修後照留並印「判不了」。我用自己的淺複製夾具跑修前版本 409ab14f,結果也是照留。所以 G1 的「修前 rc 1 一律丟」我沒重現,G1 歸因未判定,可能是 r1 另有構造。
- **夾具跨環境**:預設分支改 `master`、`trunk` 後,`-k redbase_branch_rows` 與 `-k spec_gate_redbase_green` 各 12 條全綠。淺複製與部分複製夾具都有 `★前置★` 斷言,環境不同時只會假紅,不會假綠。
- **未驗環境**:Linux、Windows、其他 git 版本沒驗。部分複製夾具在 Windows 本來就跳過。
- **測試與邊界**:
  - `-k tq_guard_cli_contract` 99 條全過,`-k tq_guard_string_comma` 24 條全過。
  - `t_name_collision_scales` 把 `_join` 改成「每次重算且不存」,以及「拿掉守衛但仍存」,兩種改壞都使 ② 紅(id 重用沒讓它假綠,1000 次呼叫約有 513 個不同 id)。
  - 未出生的 repo、分離 HEAD、斜線與中文分支名(`feat/中文`)都沒崩,結果合理。
  - 300 個不存在的 sha 在上限 200 下約 8 秒完成,印「100 筆判不了」。
  - `_TG_CONST_PAT` 對三引號邊界輸入判斷正確,100 萬字元未結尾輸入約 0.03 秒內回傳。

## 圖譜鏡頭(固定席節點)

- **lumos-cli-read**(search 預設排除 superseded 的 INVARIANT):不影響。本 diff 沒碰 search 的濾網。
- **測試假綠形態**:大致守住。S8、S7、S9、S1 都有前置。只有 S6 同名重開缺,見 finding 2。
- **design-loop、guard-kill、lifecycle**(各自的 INVARIANT):不影響。沒碰處置閘、guard kill 的 rc 與 JSON 純度、re-inject。
- **規格閘、test-guard、test-profile-multiplatform、pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger**:筆記文字與程式一致,但規格閘 WHY 寫「部分複製整批不問 git」,與 finding 1 的新式設定不符。
- **表態記錄**:`py-external satisfied` 指向 `scenario_probe.py:1077`,與本 diff 無關,我沒驗。其餘 `na` 與本 diff 範圍沒衝突。

## 三問回答

1. **原問題修復效果**:別條分支判綠漏過來的情形,新測試與我的臨時 repo 都看到被擋。同名 tag 修好。淺複製我只確認修後照留。部分複製只修了舊式設定(finding 1)。
2. **修補處的正常、錯誤、相鄰路徑**:
   - 帳進版控時不過濾的路徑照舊(S7 綠)。
   - 超過上限時先問最新的,且最新的被當祖先留下。
   - 過了截止時間照留並印數量。
   - `_redbase_attach` 先問一次 `_gov_ledger_ignored` 再寫,順序改了但沒壞。
   - 未驗相鄰路徑:時鐘倒退、真實慢遠端。
3. **新發現修前修後**:finding 1 修前舊式、新式都連遠端,修後只剩新式。finding 2 兩版皆缺前置。

最嚴重等級是 major,blocking 共 1 條。

臨時目錄仍在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/邊界-sonnet/`,內含 `tmp/`、`copy/`、`exp/`,依派工詞由編排者收貨後刪。
