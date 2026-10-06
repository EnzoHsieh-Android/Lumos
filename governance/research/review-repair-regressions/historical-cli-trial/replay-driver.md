# 原始回放driver

這是第二次完整收據執行的原始Python來源，包含固定測試斷言。查核指紋用程式圍欄的內容（末尾含換行）。重放前把repo與out換到私有clone／新結果目錄，不覆蓋原始卷證；wrapper、案例輸入與斷言不改。受控副本提交只在臨時detached工作樹，不是產品分支提交。此driver原本會寫controlled-fault.patch；本交付將該原始bytes無損base64封存，SHA不變。

```python
from pathlib import Path
import tempfile,subprocess,sys,json,hashlib
repo=Path('/tmp/lumos-future-repair-regression-research')
out=repo/'governance/research/review-repair-regressions/historical-cli-trial'
def git(*args):
    r=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,timeout=120)
    if r.returncode: raise RuntimeError(r.stderr)
    return r.stdout.strip()
versions={name:git('rev-parse',sha) for name,sha in [('before','bd9b826c'),('after','cf53b1ad'),('current','161984a0')]}
text='這是可以核對的凍結材料原文而且字數足夠'
report='severity: minor\n## F1\nseverity: minor\nblocking: 否\n引句:「'+text+'」\n'
clean_report='severity: clean\n本席沒有發現。\n'
wrapper='''import runpy,sys,hashlib
from pathlib import Path
cli=sys.argv[1]; fault=sys.argv[2]; cli_args=sys.argv[3:]
namespace=runpy.run_path(cli)
print("PROBE_LOADED_CODEFILE="+namespace["main"].__code__.co_filename,file=sys.stderr)
print("PROBE_SOURCE_SHA256="+hashlib.sha256(Path(cli).read_bytes()).hexdigest(),file=sys.stderr)
if fault=="runtime_read":
    snapshot=Path(cli_args[cli_args.index("--snapshot")+1])
    original=Path.read_bytes
    def read_bytes(path):
        if path==snapshot: raise RuntimeError("runtime-probe-read-fault")
        return original(path)
    Path.read_bytes=read_bytes
sys.argv=[cli,*cli_args]
raise SystemExit(namespace["main"]())
'''
cases=['invalid_carrier','valid_carrier','legacy_invalid','missing_snapshot','runtime_read']
records={'scope':'historical controlled CLI replay, not live review rounds or code-loop approval','versions':[],'runs':[],'probe':{'wrapper':wrapper,'sha256':hashlib.sha256(wrapper.encode()).hexdigest(),'quote':text,'quoted_report':report,'clean_report':clean_report,'cases':cases},'attribution_limits':['current also includes latest-main integration and unrelated graph/skill changes; selected cases only','before/after interval is the snapshot feature commit; not a complete regression proof','synthetic fault and mutation runs are not real review receipts or contract backing']}
created=[]
with tempfile.TemporaryDirectory(prefix='lumos-historical-cli-') as temp:
    root=Path(temp)
    def run_version(name,tree,commit):
        cli=(tree/'scripts/lumos').resolve(); digest=hashlib.sha256(cli.read_bytes()).hexdigest()
        records['versions'].append({'name':name,'commit':commit,'tree':subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD^{tree}'],text=True).strip(),'cli_sha256':digest})
        for case in cases:
            base=root/'fixtures'/name/case;v=base/'kg';v.mkdir(parents=True)
            for sub in ['Systems','Verification','Projects','MOC']:(v/sub).mkdir()
            (v/'MOC/idx.md').write_text('---\ntype: moc\n---\n# idx\n')
            snap=base/'snapshot.patch';rpt=base/'report.md'
            rpt.write_text(clean_report if case=='legacy_invalid' else report)
            if case!='missing_snapshot':snap.write_bytes(b'\xff\xfe' if case in ['invalid_carrier','legacy_invalid'] else (text+'\n').encode())
            args=['--vault',str(v),'canary','record','none','--loop','code-historical-fixture','--round','r1','--auditor','通才-codex','--tier','standard','--orchestrator','codex','--severity','clean' if case=='legacy_invalid' else 'minor','--findings','0' if case=='legacy_invalid' else '1','--report',str(rpt),'--snapshot',str(snap)]
            if case!='legacy_invalid':args+=['--findings-set','F1','--folded-set','F1','--refuted-set','none']
            cmd=[sys.executable,'-B','-c',wrapper,str(cli),'runtime_read' if case=='runtime_read' else 'none',*args]
            r=subprocess.run(cmd,cwd=base,capture_output=True,text=True,timeout=30)
            ledger=base/'.canary-log.jsonl'; rows=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
            loaded=('PROBE_SOURCE_SHA256='+digest in r.stderr and 'PROBE_LOADED_CODEFILE='+str(cli) in r.stderr)
            assert loaded, (name,case,r.stderr)
            if case=='invalid_carrier':passed=r.returncode==2 and '--snapshot' in r.stderr and 'UTF' in r.stderr and 'Traceback' not in r.stderr and not rows and '✓' not in r.stdout
            elif case in ['valid_carrier','legacy_invalid']:
                passed=r.returncode==0 and len(rows)==1 and rows[0].get('reported')==(0 if case=='legacy_invalid' else 1) and rows[0].get('snapshot_sha256')==hashlib.sha256(snap.read_bytes()).hexdigest()
            elif case=='missing_snapshot':passed=r.returncode==2 and '--snapshot' in r.stderr and 'UTF' not in r.stderr and 'Traceback' not in r.stderr and not rows
            else:passed=r.returncode==1 and 'RuntimeError: runtime-probe-read-fault' in r.stderr and not rows
            records['runs'].append({'version':name,'case':case,'role':'repair' if case=='invalid_carrier' else 'preserve','command':cmd,'cwd':str(base),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'loaded_source_verified':loaded,'assertion_passed':passed,'ledger_rows':rows,'ledger_sha256':hashlib.sha256(ledger.read_bytes()).hexdigest() if ledger.exists() else None})
            print(name,case,'rc',r.returncode,'assertion',passed,flush=True)
    try:
        trees={}
        for name,commit in versions.items():
            tree=root/name
            git('worktree','add','--detach',str(tree),commit);created.append(tree);trees[name]=tree
            assert subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()==commit
            assert (tree/'scripts/lumos').read_bytes()==subprocess.check_output(['git','-C',str(repo),'show',commit+':scripts/lumos'])
            run_version(name,tree,commit)
        tree=trees['after'];target=tree/'scripts/lumos';original=target.read_text()
        old='            except UnicodeDecodeError as e:\n                print(f"擋下:--snapshot 不是有效 UTF-8:'
        new='            except Exception as e:\n                print(f"擋下:--snapshot 不是有效 UTF-8:'
        assert original.count(old)==1
        target.write_text(original.replace(old,new))
        subprocess.run(['git','-C',str(tree),'add','--','scripts/lumos'],check=True)
        subprocess.run(['git','-C',str(tree),'-c','core.hooksPath=/dev/null','-c','user.name=Controlled fixture','-c','user.email=fixture@invalid','commit','-m','test: 受控快照例外誤分類副本'],check=True,capture_output=True)
        mutant=subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()
        patch=subprocess.check_output(['git','-C',str(tree),'diff','--no-ext-diff','--no-textconv','--no-color','--binary','--full-index',versions['after'],mutant,'--','scripts/lumos'])
        (out/'controlled-fault.patch').write_bytes(patch)
        records['mutation']={'parent_commit':versions['after'],'fixture_commit':mutant,'old':old,'new':new,'patch_sha256':hashlib.sha256(patch).hexdigest(),'limits':'private detached fixture commit, not on product branch; replay from parent plus exact saved replacement'}
        run_version('fault',tree,mutant)
        subprocess.run(['git','-C',str(tree),'checkout','--detach',versions['after']],check=True,capture_output=True)
        assert target.read_text()==original
        run_version('restored',tree,versions['after'])
    finally:
        for tree in reversed(created):
            subprocess.run(['git','-C',str(repo),'worktree','remove','--force',str(tree)],check=True,capture_output=True,timeout=120)
by={name:[r['assertion_passed'] for r in records['runs'] if r['version']==name] for name in ['before','after','current','fault','restored']}
records['expected_assertion_patterns']=by
records['cleanup']='all self-created worktrees removed; temporary fixture root cleaned'
(out/'experiment.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
assert by=={'before':[False,True,True,True,True],'after':[True]*5,'current':[True]*5,'fault':[True,True,True,False,False],'restored':[True]*5},by
print('25 observations captured; same product/case expectations; own temporary worktrees cleaned',flush=True)
```
