severity: major
seat: 外家否決4-codex

## F1 CI 掃描會把多行腳本內容當 YAML 設定，兩層 doctor 都可能靜默漏報

severity: major
blocking: 是 — 淺層 checkout 會讓兩道檢查直接跳過；doctor 若被腳本文字騙過，CI 後盾實際不存在卻不會警告。
引句:「if needle in text and "fetch-depth: 0" not in text:」
file: `scripts/lumos:25046`

具體失敗場景：工作項目確實呼叫 `note-audit check`，但 checkout 沒設完整歷史；另一個 `run: |` 腳本只要含有 `fetch-depth: 0` 字樣，函式就誤認為該 job 已抓完整歷史，回傳空清單。合法的 `jobs: # "all jobs"` 行尾註解也不會被目前正則移除，使整個 `jobs` 區塊無法辨識。`_note_shape_doctor_lines` 與 `_note_audit_doctor_lines` 共用此結果，因此一起漏報。

最小重現：

```sh
python3 -c "import runpy; m=runpy.run_path('scripts/lumos'); b='jobs:\n  audit:\n    steps:\n      - uses: actions/checkout@v4\n      - run: |\n          echo fetch-depth: 0\n      - run: python3 scripts/lumos note-audit check --diff x\n'; F=type('F',(),{'name':'block.yml','read_text':lambda self,encoding=None,errors=None:b}); print(m['_ci_jobs_calling_without_full_history']([F()],'note-audit check'))"
```

輸出：

```text
[]
```

預期應回 `[("block.yml", "audit")]`。解析必須排除 block scalar 內容，且只把 checkout step 的 `with.fetch-depth` 當設定，不能對整個 job 做字串搜尋。

## F2 decision-amend 在已追蹤的 D+A 搬檔上會放過已推決策

severity: major
blocking: 是 — 已推上遠端的決策可在本機搬檔並大幅改寫後被當成未推決策直接修改，破壞只能以 supersede 翻案的合約。
引句:「if untracked:」
file: `scripts/lumos:24920`
file: `scripts/lumos:24940`

具體失敗場景：遠端 `Old.md` 已有 `d1`；本機把它搬成 `Fresh.md` 並大幅改寫，使 `git diff -M` 低於相似度門檻而輸出 `D Old.md`、`A Fresh.md`。只要新檔已 staged 或本機提交過，`ls-files` 便令 `untracked=False`，新增的純刪除防線完全不執行；後續改名表為空，只查不存在的 `ref:Fresh.md`，最後錯誤印出「這條決策還沒推上去」並允許修改。

最小重現以真實函式注入上述 `git --name-status -z -M` 輸出：

```sh
python3 -c "import runpy,pathlib,subprocess; d=runpy.run_path('scripts/lumos'); g=d['cmd_decision_amend'].__globals__; root=pathlib.Path('.').resolve(); E=type('E',(),{'vault':root/'docs/lumos-toolchain-knowledge'}); CP=subprocess.CompletedProcess; g['_lens_git']=lambda rr,*a,**k: CP(a,0,str(root)+'\n','') if a[:2]==('rev-parse','--show-toplevel') else CP(a,0,'origin\n','') if a==('remote',) else CP(a,0,'Fresh.md\n','') if a[:2]==('ls-files','--error-unmatch') else CP(a,0,'','') if a[:2]==('fetch','--all') else CP(a,0,'refs/remotes/origin/main\n',''); g['_ns_git']=lambda rr,*a:b'D\0docs/lumos-toolchain-knowledge/Systems/Old.md\0A\0docs/lumos-toolchain-knowledge/Systems/Fresh.md\0'; g['_nodehome_cat_blobs']=lambda rr,specs:[None]; lines=['---','decisions:','  - id: d1','    decided: 2026-09-01','    context: pushed text','---','# Fresh']; g['load_raw_for_edit']=lambda path:(lines,0,5); g['atomic_write_verify']=lambda *a,**k:None; print('rc='+str(d['cmd_decision_amend'](E(),'Systems/Fresh.md','d1','context','changed')))"
```

輸出：

```text
✓ decision-amend Systems/Fresh.md d1.context 改好了(這條決策還沒推上去)
rc=0
```

純刪除歧義不能只在 `untracked` 分支檢查；至少應檢查被刪遠端 blob 是否含相同決策編號，無法確認時拒絕。

## F3 64 位全零會回傳 SHA-1 空樹，令 SHA-256 code-loop fail-open

severity: major
blocking: 是 — SHA-256 repo 的新分支首推若找不到遠端主線，代碼審風險判定會收到無效範圍；`pitfalls` 非零後明確走 fail-open，high 變更可沒有留痕仍放行。
引句:「_ZERO_SHA_RE = re.compile(r"0{40}|0{64}")」
file: `scripts/lumos:29183`
file: `scripts/lumos:30960`
file: `scripts/lumos:31843`

具體失敗場景：新常數認得 64 個零，但 `_lens_push_base` 找不到主線時仍回傳硬編碼的 40 位 SHA-1 空樹 `4b825d…`。在 SHA-256 repo，這不是合法物件；code-loop 隨後把該範圍交給 `pitfalls`，失敗即 `blocked=False`。

最小重現：

```sh
python3 -c "import runpy; d=runpy.run_path('scripts/lumos'); g=d['_lens_push_base'].__globals__; g['_mainline_ref']=lambda *_a,**_k:None; b,w=d['_lens_push_base']('.', '0'*64, 'f'*64); print(b,len(b),w,sep=' | ')"
```

輸出：

```text
4b825dc642cb6eb9a060e54bf8d69288fbee4904 | 40 | 新分支首推:找不到主線,從空樹算(截到上線點)
```

空樹需依 repo object format 動態取得，並同步修正 `_bound_tests_range` 與 code-loop 對空樹的辨識；只擴充全零正則不足以支援 SHA-256。

最嚴重 severity: major；blocking 共 3 條。