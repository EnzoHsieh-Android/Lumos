severity: minor

**1. 分層與依賴方向**
修補後沒有跨層直呼。
- 走訪跳過清單改成 `CODE_SKIP_DIRS | {".gradle"}`。這跟 `_walk_test_files` 用同一份共用清單的做法一致,上一輪的 major 已收掉。
  - 對照:`scripts/lumos:6059`、`scripts/lumos:6806`。
- 基準檔讀取改走 `_choice_cov_read`,不再自己 `open`。
  - 對照:`scripts/lumos:79999`。
- `_KillPrep._src_pkgs` 快取欄位放在 `__init__`,用 `{}` 字典,以平台根為鍵。這跟 `self._cmd = {}`(`scripts/lumos:29207`)、`self._cache = {}`(`scripts/lumos:9993`)的寫法一致。
- `_measure` 裡是「不在就算、再取用」的惰性寫法。它在 `_KillPrep` 內部,沒有跨類別。
- 走訪用 `followlinks=False`,跟 `scripts/lumos:42401` 一致。
- 函式內 `import math` 在這個檔案很常見(`scripts/lumos:5209`、`scripts/lumos:22096`、`scripts/lumos:29394`、`scripts/lumos:70857`),不算新做法。

**2. 命名與錯誤處理**

`store` 的兩段 try 結構對。第二段基準檔寫失敗就吞掉,是有意的降級。

這裡有一條不對齊,見 finding 1。

這一問的其他點都對齊:
- 看滿上限印 `⚠ …` 到 `file=sys.stderr`,跟 `scripts/lumos:51648` 的寫法一致。
- 兩個新常數 `_CHOICE_COV_SRC_ENTRIES`、`_CHOICE_COV_SRC_HEAD`,以及 `_CHOICE_COV_BASE_MAX`,都沿用 `_CHOICE_COV_*` 前綴。
- `except OSError` 的粒度跟鄰居一致。

**3. 第二種做法**

這條不算新增第二種做法,只是測試造樣板的寫法跟鄰居不同(finding 1)。

- 測試用 `_choice_cov_src_pkgs(tmp)` 直呼加 `redirect_stderr`,跟檔內其他測試的 `io.StringIO` 加 `contextlib.redirect_stderr` 一致。
- 暫時改 `m._CHOICE_COV_SRC_MAX` 並在 `finally` 還原,跟 `scripts/test_lumos.py:147224`、`scripts/test_lumos.py:147238` 的做法一致。
- `t_choice_cov_resume_old_cache` 用 `_ckc_repo`、`_ck_run`、`_ck_cleanup`,是對的。
- `t_choice_cov_base_read_rejects` 用 `_ckc_cb_stub`,是對的。

finding 1
severity: minor
blocking: 否
引句:「        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(outside, ignore_errors=True)」
對照:`scripts/test_lumos.py:144203` 的 `_ck_cleanup(*paths)` 是 ckc 系列測試清暫存的統一入口。
- 新的 `t_choice_cov_src_pkgs_edges` 與 `t_choice_cov_base_read_rejects` 各自在函式裡 `import shutil` 再直呼 `shutil.rmtree`。
- 同系列的 `t_choice_cov_proj_pkgs` 與 `t_choice_cov_resume_old_cache` 都走 `_ck_cleanup`。
- 這是輸出與清理寫法跟鄰居不一致,結構沒壞,所以列 minor。

不對齊共 1 條,其中 major 0 條。

(派工詞說要檢查的鎖檔 `.warming`:`/Users/enzo/.cache/lumos/dispatch-lens/` 下沒看到該檔,我沒動鎖,照派工詞審查完。)
