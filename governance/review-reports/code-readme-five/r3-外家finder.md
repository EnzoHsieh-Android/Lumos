severity: major
blocking: 是
引句:「path="${path:1:${#path}-2}"; path="${path//\\\"/\"}"; path="${path//\\\\/\\}"; path="${path//\\t/$'\t'}"」
file: `scripts/hooks/pre-commit:127`; `scripts/hooks/post-commit:52`
場景: 新增無副檔名 shebang 檔 `bin/weird\x01tool` 時，Git 以 `"bin/weird\\001tool"` 輸出，但解碼器不處理八進位 escape，導致 `git show` 找不到而讓 pre-commit 放行、post-commit 也不記錄；可翻紅重現是在現有測試加入 `r2f = run({"bin/weird\x01tool": "#!/bin/sh\necho\n"})` 並斷言 `r2f.returncode != 0`，現碼會失敗。

max severity: major
