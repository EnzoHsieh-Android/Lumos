severity: minor

# 架構對齊審查——code-clause-bindings(r2,末輪驗收,sonnet)

被審:全量 `governance/review-reports/code-clause-bindings/r2-snapshot.patch`;delta `governance/review-reports/code-clause-bindings/r2-delta.patch`。
只判前輪(r1)六條 finding 折入後對不對齊,以及折入本身有沒有引入新的第二種做法。不找 bug、不評風格。

★核對方法備註★:工作區 `scripts/lumos` 目前混有另一個 session 未提交的改動(`_extra_fm_keys`/`_scope_policy`,3799-3944 行一帶,與本案無關——正是圖譜〈同工作區 git add 的夾帶風險〉記過的同款情境)。已核對 `git rev-parse HEAD:scripts/lumos` = `e11de2b9156797040ec4928ba9dd08afae50c24e`,與 r2-snapshot.patch 收尾的目標 blob(`index fb4a183..e11de2b`)一致,所以下面全部 file:line 對照的是 `git show HEAD:scripts/lumos`(=r2-snapshot 的結果態),不是髒工作區——两者在條款綁定相關行號一致,但不是同一份檔案物件,特此註記。

LUMOS-IMPACT: Lumos/main..HEAD

---

## 1. 分層與依賴方向

**判定:對齊。**

r1 這一條(major):`_clause_bindings_for` 把顯式 `root` 蓋掉、只要 `env` 不是 None 就無條件用 `_vault_repo_root(env)` 反推,跟 `_dsp_root`(`scripts/lumos:6682`)等十餘處「顯式覆蓋優先、env 反推只是預設」的既有優先序相反。

折入後:

> 引句:「rr = Path(root) if root else _vault_repo_root(env)」

順序倒回來了——`root` 有值就贏,沒有才退回 `_vault_repo_root(env)`,跟 `_dsp_root = Path(repo).resolve() if repo else _vault_repo_root(env)`(file: `scripts/lumos:6682`)同一條「顯式贏」規則。修法本身附的理由行也點名了這正是照抄既有慣例:

> 引句:「(r1 架構席/單reviewer 都抓到我寫反了:git-less 部署副本裡 .git 不在,反推會落錯根)」

往上游追一層:`_disposal_clause_step` 拿到的 `root` 就是 `_loop_status_disposal` 收到的那個 `root` 參數,而它的唯一呼叫端已經是 `_dsp_root`(file: `scripts/lumos:6682-6683`,`_loop_status_disposal(rounds, loop_id, spec, n_badlines, _dsp_root, ...)`)——換句話說,`_clause_bindings_for` 現在收到的 `root` 本來就已經是照「顯式 --repo 優先」規則解過的 `Path` 物件,`Path(root) if root else ...` 這一行只是原樣尊重它,沒有第二次判斷邏輯、沒有跨層繞過。三個呼叫端(`cmd_spec_trace`、`_handoff_clause_counts`、`_disposal_clause_step`)裡只有處置閘那個真的有 `--repo` 語境會傳 `root`,另兩個維持不傳(退回 env 反推)——這個分工跟 r1 原本判定「對齊」的那一半(env→index 轉接層)一致,沒有變。

- severity: major(r1 原評級,現已折平)
- blocking: 否(已解決)

---

## 2. 命名與錯誤處理

**判定:不對齊(1 條沿用 r1、1 條本輪新增,均 minor)。**

r1 finding「docstring 未改」(minor):`cmd_spec_trace` 的函式頭已經同步改成裁決語意:

> 引句:「× 回指 Verification 的認領(舊制對照欄)。rc:有未標條款=1;全標(綁了/靠人,懸空只提醒)=0;計劃無 [SN]=0(opt-in 未啟用)。唯讀。」

跟程式碼 `return 1 if untagged else 0`(file: `scripts/lumos:4222`)語意一致,舊制「全認領/有未認領」的講法已經拿掉。同時 `HELP_WHEN["spec-trace"]` 與 `argparse` 的 `help=` 也一併同步改了(這兩個 r1 原本沒點名,算折入時順手做齊,不倒退)。**已對齊。**

- severity: minor
- blocking: 否

r1 finding「spec 讀不到處置不一致」(minor):`_loop_status_disposal` 的 G3 步驟(file: `scripts/lumos:13513-13517`)遇到 `--spec` 讀不到是 `擋下:--spec 指的文件讀不到...` 直接 `return 2`;而新第五步遇到同一種失敗(計劃檔讀不到)原本印「計劃讀不成文字」、當成軟性 `fail`,由呼叫端 `fails.append` 繼續跑完其他步。折入後:

> 引句:「print(f"[disposal] 條款綁定: ✗ — --spec 指的文件讀不成文字({e.__class__.__name__}),確認路徑對不對:\n    {spec}")」

只把訊息措辭改成貼近 G3 那句(「確認路徑對不對:\n    {spec}」是照抄 G3 的句型),但 **回傳值仍是 `"fail"` 不是中斷整個函式的 rc2**——同一函式裡「用法錯誤,rc2 立刻結束」vs「處置未過,繼續跑完其他四步再彙總」這兩條規則本身沒有被拉齊,只是外觀更像而已。r1 原本就註明這是描述兩套規則不一致、不是說一定會同時觸發(實務上 G3 排在第一步,通常會先攔到,第五步這條 except 路徑近乎打不到)——這個前提沒變,折入沒有解決根本的控制流分歧,只是把症狀(措辭不一致)蓋掉了一半。**仍不對齊,原因是修法只動了訊息文字、沒有動兩者的 rc 語意分歧本身。**

- severity: minor
- blocking: 否

本輪新增(minor,由這次折入本身帶出來的):`_disposal_clause_step` 的 docstring 講「skip 四種」,但折入「外家席 major:副檔名跳過可繞」時新增了 `kind is None`(loop 編號看不出是設計審還是代碼審)這第五條 skip 路徑,docstring 沒有算進去:

> 引句:「skip 四種:①凍結/回放模式(spec_sha_override 有值,對凍結 sha 判、不重讀活檔)②迴圈類型是 code(loop id 前綴 code-,同 _roster_kind;」

程式碼裡緊接著:

> 引句:「if kind is None:」

這一分支(file: `scripts/lumos:13413-13415`)印出理由句、`return "skip"`,是貨真價實的第五種 skip,但 docstring 的「①②③④」編號只到四、沒有把它算進總數也沒有給它編號——跟 r1 原本抓到 `cmd_spec_trace` docstring 沒跟上實作是同一類問題(自我文件跟不上這次改動新增的分支),只是這次出現在另一個函式的 docstring,而且是這次折入才新產生的,不是 r1 六條裡的哪一條。

- severity: minor
- blocking: 否

---

## 3. 第二種做法

**判定:對齊(r1 三條全部折平,未發現新的第二種做法)。**

r1 finding「標記家族 major」:`[manual:]` 宣稱跟 `[test:]`/`[audit:]` 同一個標記家族,但原本沒被收進 `INV_TAG_RE`、定義位置也離那一叢很遠。折入後,定義搬到 `AUDIT_REF_RE` 正下方(跟 `TEST_REF_RE`/`AUDIT_REF_RE` 同一叢,file: `scripts/lumos:3027-3036`),原本挨著 `SPEC_CLAUSE_RE` 的那份重複定義被拿掉了,且真的收進聯集正則:

> 引句:「MANUAL_REF_RE = re.compile(r"\[manual:\s*([^\]]*)\]")」

> 引句:「INV_TAG_RE = re.compile(r"\[(?:test|audit|kill|src|git|manual):\s*[^\]]*\]")」

`strip_test_refs`(file: `scripts/lumos:3381-3383`)靠 `INV_TAG_RE` 一次剝乾淨,`[manual:]` 現在真的會被一起剝掉,不再是「文字上認親、結構上沒收編」的第三種處理。`[^\]]+` 放寬成 `[^\]]*` 也是配合 `MANUAL_REF_RE` 允許空內容(用來判「太短視同未標」)的必要連動,不是額外分歧。**已對齊,而且是完整折平(定義位置+聯集收編兩件事都做了),不是只改註解。**

- severity: major(r1 原評級,現已折平)
- blocking: 否(已解決)

r1 finding「cutoff 當日制 minor」:原本 `_CLAUSE_GATE_SINCE = "2026-09-08"` 用當日,跟 `_SEV_WRITESIDE_CUTOFF` 的「隔日制」慣例(合入當天白天舊碼寫的帳,日粒度切不開先後)矛盾。折入後:

> 引句:「_CLAUSE_GATE_SINCE = "2026-09-09T00:00:00+08:00"   # 處置閘的條款綁定步只看首筆帳在這之後的迴圈——不回溯舊迴圈(週跑回放會重跑閘,回溯=舊判定全翻)。」

改成隔日(合入日 09-08 的次日 09-09),且比對方式從裸字串切片改成透過既有的 `_loop_ts_key`(file: `scripts/lumos:5915-5931`,這支函式在這次改動之前就已經存在,是「派工編制」那條線帶進來的既有共用工具,不是本次新造)換算 UTC 秒數再比——比 `_SEV_WRITESIDE_CUTOFF` 自己在別處仍用的裸字串比較(file: `scripts/lumos:4831`、`scripts/lumos:13714` 的 `str(hit.get("ts", "")) >= _SEV_WRITESIDE_CUTOFF`)更嚴謹。**這不是引入第二套 cutoff 機制**——`_loop_ts_key` 本來就是全庫共用的單一時間比較工具,這裡只是多一個呼叫端開始用它,`_SEV_WRITESIDE_CUTOFF` 自己沒改用只是既有技術債、跟本次折入無關,不倒扣。⚠ 這裡我判斷「不算新分歧」是因為工具本身唯一、只是採用點還沒全部遷移過去,如果之後有人主張這也算「同一件事兩種比法並存」,盼人工複核這一小段。

- severity: minor(r1 原評級,現已折平)
- blocking: 否(已解決)

r1 finding「提醒排版 minor」:`_disposal_clause_step` 的 FAIL 分支原本分兩行印(為什麼在意 / 怎麼補),`cmd_spec_trace` 原本揉成一行,同一份 patch 兩種排版。折入後兩處變成逐字相同:

> 引句:「print("    每條要嘛在那一行綁 [test:測試名],要嘛寫 [manual:一句怎麼驗];沒有測試可掛也得講清楚靠人怎麼驗")」

這行在 `cmd_spec_trace`(file: `scripts/lumos:4221`)與 `_disposal_clause_step`(file: `scripts/lumos:13449`)兩處逐字相同(含縮排),`cmd_spec_trace` 上面那句「為什麼在意」也拆成獨立一行印,不再跟補救辦法揉在同一句。**已對齊。**

- severity: minor(r1 原評級,現已折平)
- blocking: 否(已解決)

---

## 小結

不對齊共 2 條,其中 major 0 條。
