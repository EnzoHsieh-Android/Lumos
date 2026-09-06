severity: major
- [major] 消費端執行時，`LUMOS_HOME` 會被指向消費端專案本身，讓來源版本檢查拿 vendored 副本和自己比較，可能把過期工具誤判為 active
  引句:「os.environ["LUMOS_HOME"] = str(Path(GRAPHCTL).resolve().parent.parent)」
  位置:scripts/test_lumos.py:22845
  blocking:是
  why:輸入是 vendored 到 `<consumer>/scripts/test_lumos.py` 與 `<consumer>/scripts/lumos` 的測試檔；預期 `LUMOS_HOME` 指向真正工具鏈來源，或來源不可達時由 `_SrcOnly` 跳過；實際解析結果是 `<consumer>`。`t_enforcement_vendored_uptodate_active` 因而讀 `<consumer>/scripts/lumos` 的版本，再用同一來源判定消費端 vendored CLI，無法驗出它相對真正來源已過期。

- [major] skip 超過基準線只印警告、不增加 `FAIL`，所以覆蓋退化仍以成功狀態碼離開
  引句:「if not _args.keyword and SKIP > _EXPECTED_SKIP_MAX:」
  位置:scripts/test_lumos.py:22965
  blocking:是
  why:輸入是全套測試中一支原本可跑的測試因環境錯誤改走 `_SrcOnly`；預期既然基準線用來阻止「沒驗到卻全綠」，超標應令退出碼非零；實際程式只 `print`，最後仍執行 `return 1 if FAIL else 0`。當 `FAIL == 0` 時 CI/pre-push 仍收到 rc=0。Windows或消費端的合理 skip 又固定觸發同一警告，久而久之也容易把真正覆蓋退化淹沒。

- [minor] `-k` 選不到測試的早退發生在建立隔離根之後、共同收尾之前，每次錯拼 keyword 都會留下完整根目錄
  引句:「_run_root = _isolate_environment()」
  位置:scripts/test_lumos.py:22898
  blocking:否
  why:輸入為 `python3 scripts/test_lumos.py -k no-such-test`；預期建立過的隔離根無論正常、早退或中斷都經同一個 `finally` 收尾；實際在零匹配分支直接 `return 1`，不寫 `.finished`、不刪 `_run_root`。`KeyboardInterrupt`、`SystemExit` 或測試迴圈外的例外也同樣繞過尾段，只能等待一天後被後續 runner 修剪。

- [clean] 抽查改動後的 HOME 相關測試，未發現因空 HOME 令新增 install 斷言恆真的情況
  引句:「check("★前置★ 現場成立:跑在拋棄式家目錄裡(不是真機)", "gctl-run-" in str(home), str(home))」
  位置:scripts/test_lumos.py:380
  blocking:否
  why:實讀兩支 install 測試及 enforcement 的來源可達／不可達案例；兩支 install 測試先確認隔離現場，再執行 `lumos install --force`，最後檢查實際生成的 CLI 與 Claude/Codex skill 路徑，不是只斷言原本為空。發現的消費端假綠另列為第一條。

- [clean] 共有 183 個 subprocess 呼叫顯式傳 `env=`；僅一個直接子進程環境沒有從 `os.environ` 複製，但該案例不會建立暫存檔
  引句:「os.environ["TMPDIR"] = str(root)」
  位置:scripts/test_lumos.py:22830
  blocking:否
  why:逐一掃描 subprocess 的 `env=` 呼叫與其環境建構；182 個直接或間接保留父環境，因此繼承 `HOME`、`USERPROFILE`、`TMPDIR` 與清除後的 `CODEX_HOME`。唯一例外是 `t_slim_get_missing_git` 的 `{"HOME": ..., "PATH": empty_bin}`；它用絕對 bash 路徑啟動 `get.sh`，隨即在 `command -v git` 失敗並退出，未走 clone、install 或 mktemp 分支，所以目前沒有逸出隔離的暫存產物。

- [clean] shell 與 git 子進程一般會收到 `TMPDIR`；被測腳本中未找到硬編碼 `/tmp` 或另行 `mktemp` 的逸出點
  引句:「# ① 暫存:之後所有 tempfile.mkdtemp() 與子進程的 TMPDIR 都落在這一輪的根底下」
  位置:scripts/test_lumos.py:22828
  blocking:否
  why:檢查測試檔及其呼叫的 hooks、slim shell 腳本；Python 父進程由 `tempfile.tempdir` 定向，繼承環境的 shell/git 由 `TMPDIR` 定向。唯一丟失 `TMPDIR` 的 subprocess 是上述「缺 git」負向案例，且在任何暫存操作前退出。

- [clean] 舊根修剪條件沒有按數量誤刪活躍平行 runner，`.finished` 的寫入順序也只會暴露已完成的根
  引句:「if not e.name.startswith("gctl-run-") or not e.is_dir(follow_symlinks=False):」
  位置:scripts/test_lumos.py:22856
  blocking:否
  why:修剪只接受系統暫存目錄直下一層、名稱為 `gctl-run-*` 且本身不是 symlink 的目錄；刪除條件是已有 `.finished` 或根目錄 mtime 超過一天。正常 runner 在全部測試及摘要完成後才寫 `.finished`，随后立即 rmtree；平行修剪者即使在兩步之間介入，也只會刪除已经完成使用的根。未找到會把新建的另一輪根判 old 的正常執行路徑。

- [clean] `_args` 在正常抵達尾段時一定存在；問題是早退與非局部例外繞過尾段，不是未初始化引用
  引句:「_args, _ = _p.parse_known_args()」
  位置:scripts/test_lumos.py:22897
  blocking:否
  why:控制流先解析 `_args`，再建立 `_run_root`，最後才讀 `_args.keyword` 或 `_args.keep_tmp`；因此尾段不存在 `UnboundLocalError`。收尾覆蓋不足已獨立列為 minor。
