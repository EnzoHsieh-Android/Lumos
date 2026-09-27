severity: major

## F1 程式檔改名後，新路徑不會喚醒既有引用
severity: major
blocking: 是 —— 違反 S12 明列的「改名」情境，應擋的舊行號引用會直接放過。

引句:「# 2) 新程式檔喚醒舊引用(筆記這次沒改也查;上線點版本裡就有的那行是舊帳,不算)」

具體輸入：上線後先寫下 `src/new.py:3`；之後執行 `git mv src/old.py src/new.py`。`_nodehome_changes` 回傳 `R old→new`，但 `prev = old or new` 令檢查轉去確認舊路徑；因 `old.py` 本來就是程式檔，`new.py` 不會加入 `became`。  
file: `scripts/lumos:23689`

最小重現：

```bash
python3 -c "import importlib.machinery as M,importlib.util as U; L=M.SourceFileLoader('x','scripts/lumos'); S=U.spec_from_loader(L.name,L); m=U.module_from_spec(S); L.exec_module(m); m._nodehome_changes=lambda r,b,t:[('R','src/old.py','src/new.py')]; m._nodehome_list=lambda r,w:({'src/old.py':'100644'},[]) if w=='BASE' else ({'src/new.py':'100644'},[]); m._nodehome_reader=lambda r,w:(lambda p:b'x=1\n'); got=m._ns_became_code(None,'BASE','TIP',m._nodehome_reader(None,'TIP')); print('expected=[src/new.py] actual=',got); assert got==['src/new.py']"
```

輸出：

```text
expected=[src/new.py] actual= []
AssertionError
```

## F2 新程式檔喚醒會漏掉單一檔名引用
severity: major
blocking: 是 —— S1 支援唯一單一檔名，但 S12 的喚醒路徑只看完整路徑，兩步提交可繞過守衛。

引句:「if not any(x in text for x in became):」

具體輸入：檔案不存在時先寫 `new.py:3`；之後新增唯一的 `src/new.py`。`became` 只有 `src/new.py`，所以全文預篩在 `new.py:3` 上為假；即使移除預篩，後面的抽取也沒有傳 `singles=[]`。  
file: `scripts/lumos:23760`  
file: `scripts/lumos:23771`

最小重現：

```bash
python3 -c "import importlib.machinery as M,importlib.util as U; L=M.SourceFileLoader('x','scripts/lumos'); S=U.spec_from_loader(L.name,L); m=U.module_from_spec(S); L.exec_module(m); q=chr(96); note='docs/kg-knowledge/Systems/A.md'; blob=('---\ntype: system\n---\n# A\n見 '+q+'new.py:3'+q+'\n').encode(); data={'TIP':{'src/new.py':b'a\nb\nc\n',note:blob},'GL':{note:b'---\ntype: system\n---\n# A\n'}}; m._nodehome_list=lambda r,w:({'src/new.py':'100644',note:'100644'},[]); m._nodehome_reader=lambda r,w:(lambda p:data.get(w,{}).get(p)); m._ns_range_added=lambda *a:(set(),[]); m._ns_became_code=lambda *a:['src/new.py']; m._nodehome_golive=lambda *a:'GL'; m._nodehome_cat_blobs=lambda *a:[blob]; got=m._note_shape_eval(None,False,'BASE','TIP','docs/kg-knowledge'); print('expected one wake violation, actual=',got); assert got[0]"
```

輸出：

```text
expected one wake violation, actual= ([], [])
AssertionError
```

## F3 無副檔名且含 @ 的真程式檔被誤拆成釘版本
severity: major
blocking: 是 —— 新增的解析規則會同時讓 note-shape 漏擋，並改壞既有 refcheck 對合法檔名的判定。

引句:「if "@" in last and "." not in last.rsplit("@", 1)[1]:」

具體輸入：受版控檔 `scripts/run@v2` 以 `#!` 開頭，筆記新增 `scripts/run@v2:2`。抽取器把真路徑拆成 `scripts/run` 加 pin `v2`；note-shape 因 `scripts/run` 不存在而放過，refcheck 則會報 missing。  
file: `scripts/lumos:19911`

最小重現：

```bash
python3 -c "import importlib.machinery as M,importlib.util as U; L=M.SourceFileLoader('x','scripts/lumos'); S=U.spec_from_loader(L.name,L); m=U.module_from_spec(S); L.exec_module(m); q=chr(96); files={'scripts/run@v2':'100755'}; pins=[]; parsed=m._node_code_ref_tokens('見 '+q+'scripts/run@v2:2'+q,{'scripts'},pins=pins); got=m._ns_check_line('.', '見 '+q+'scripts/run@v2:2'+q, 'body', files, lambda p:b'#!/bin/sh\necho ok\n', {'scripts'}, {'run@v2':['scripts/run@v2']}); print('抽取=',parsed,pins); print('expected violation, actual=',got); assert got"
```

輸出：

```text
抽取= ([], set()) [('scripts/run', '2', 'v2')]
expected violation, actual= []
AssertionError
```

## F4 合併時改名會把 parent 帶入的行誤判成合併新寫
severity: major
blocking: 是 —— 違反 S5「從任一上一版帶進來不應擋」，會硬擋正常合併。

引句:「specs += [f"{pp}:{p}" for pp in parents]」

具體輸入：第一個 parent 使用 `B.md` 且沒有引用；第二個 parent 的 `A.md` 已有引用；合併把 `A.md` 政名為 `B.md` 並保留該行。實作拿合併後的 `B.md` 去讀每個 parent，第二個 parent 讀不到，於是把它已有的行算成全新。  
file: `scripts/lumos:23593`

最小重現：

```bash
python3 -c "import importlib.machinery as M,importlib.util as U; L=M.SourceFileLoader('x','scripts/lumos'); S=U.spec_from_loader(L.name,L); m=U.module_from_spec(S); L.exec_module(m); p='docs/kg-knowledge/Systems/B.md'; bad=b'bad '+bytes([96])+b'src/a.py:2'+bytes([96]); m._nodehome_git=lambda *a:b'M P1 P2\n'; m._ns_git=lambda *a:(p+'\0').encode(); seen=[]; m._nodehome_cat_blobs=lambda r,s:(seen.extend(s) or [bad+b'\n',b'',None]); got=m._ns_range_added(None,'P1','M','docs/kg-knowledge',exclude_remote=False); print('requested=',seen); print('expected texts=set() actual=',got[0]); assert got[0]==set()"
```

輸出：

```text
requested= ['M:docs/kg-knowledge/Systems/B.md', 'P1:docs/kg-knowledge/Systems/B.md', 'P2:docs/kg-knowledge/Systems/B.md']
expected texts=set() actual= {'bad `src/a.py:2`'}
AssertionError
```

## F5 新增行只按文字全域回配，會誤擋另一篇的舊行
severity: major
blocking: 是 —— 違反 S1「沒改動的舊行不應擋」，而且是硬閘誤擋。

引句:「texts.update(t_.strip() for _n, t_ in rows if t_.strip())」

具體輸入：提交一曾在 A.md 新增 `src/a.py:2`，提交二又刪掉；B.md 在範圍前已有完全相同的舊行，本次只新增乾淨文字。`texts` 是跨檔案的純文字集合，最終掃 B.md 時會把其舊行當成 A.md 曾新增的行。  
file: `scripts/lumos:23584`  
file: `scripts/lumos:23737`

最小重現：

```bash
python3 -c "import importlib.machinery as M,importlib.util as U; L=M.SourceFileLoader('x','scripts/lumos'); S=U.spec_from_loader(L.name,L); m=U.module_from_spec(S); L.exec_module(m); q=chr(96); note='docs/kg-knowledge/Systems/B.md'; bad='見 '+q+'src/a.py:2'+q; blob=('---\ntype: system\n---\n# B\n'+bad+'\n本次真正新增的是乾淨行\n').encode(); m._nodehome_list=lambda r,w:({'src/a.py':'100644',note:'100644'},[]); m._nodehome_reader=lambda r,w:(lambda p:{'src/a.py':b'a\nb\n',note:blob}.get(p)); m._ns_range_added=lambda *a:({bad,'本次真正新增的是乾淨行'},[note]); m._ns_became_code=lambda *a:[]; got=m._note_shape_eval(None,False,'BASE','TIP','docs/kg-knowledge'); print('expected=[] actual=',got[0]); assert got[0]==[]"
```

輸出：

```text
expected=[] actual= [('docs/kg-knowledge/Systems/B.md', 5, '程式行號引用', '`src/a.py:2`', ...)]
AssertionError
```

## F6 壞釘版本會誤擋明文豁免的 Markdown 引用
severity: major
blocking: 是 —— S1 明訂指向 `.md` 不應擋，但新增條件只驗「路徑存在」，沒有先限制為程式檔。

引句:「if l and p in files and not _pin_ok(p, l, s):」

具體輸入：新增 `docs/lumos-toolchain-knowledge/MOC/index.md@HEAD:5`。未釘版本的 `.md:5` 會放行，但只要帶 `@HEAD`，便因 Markdown 路徑存在而被列成「釘版本不合法」。  
file: `scripts/lumos:23647`

最小重現：

```bash
python3 -c "import importlib.machinery as M,importlib.util as U; from pathlib import Path; L=M.SourceFileLoader('x','scripts/lumos'); S=U.spec_from_loader(L.name,L); m=U.module_from_spec(S); L.exec_module(m); root=Path('.').resolve(); sha=m._lens_full_sha(root,'HEAD'); reader=m._nodehome_reader(root,sha); files=m._nodehome_list(root,sha)[0]; top={x.split('/',1)[0] for x in files if '/' in x}; q=chr(96); got=m._ns_check_line(root,'見 '+q+'docs/lumos-toolchain-knowledge/MOC/index.md@HEAD:5'+q,'body',files,reader,top,{}); print('expected=[] actual=',got); assert got==[]"
```

輸出：

```text
expected=[] actual= [('釘版本不合法', '`docs/lumos-toolchain-knowledge/MOC/index.md@HEAD:5`', ...)]
AssertionError
```

總結:最高 severity major，blocking 6 條。