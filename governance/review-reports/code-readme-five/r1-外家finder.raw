severity: major
blocking: 是
引句:「[[ "$first" =~ ^#!.*(python|bash|zsh|node|ruby|perl|/sh|[[:space:]]sh) ]]」
file: `scripts/hooks/pre-commit:126`、`scripts/hooks/post-commit:51`
場景: 合法且常見的無副檔名 `#!/bin/dash` 腳本不匹配，pre-commit 會把唯一程式碼改動當成「沒 code」放行，post-commit 也不記 bypass；最小重現: `bash -lc 's="#!/bin/dash"; [[ "$s" =~ ^#!.*(python|bash|zsh|node|ruby|perl|/sh|[[:space:]]sh) ]]; echo rc=$?'` 輸出 `rc=1`。

max severity: major
