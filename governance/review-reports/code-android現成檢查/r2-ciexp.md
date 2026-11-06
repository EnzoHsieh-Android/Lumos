# A1 證據模型實測(2026-11-06)

做法:用 gh api 下載下列 6 個公開 Android 專案 `.github/workflows/` 底下的 .yml/.yaml(每個最多 12 支),經 lumos 的 `_ci_workflow_texts` 去註解後交給 `_android_ci_lint_evidence`;同時列出被認成跡象的詞。

```
TeamNewPipe_NewPipe: 有跡象 跡象詞=['build', 'lintContinuous']
android_architecture-samples: 找不到(會印 A1) 跡象詞=[]
android_nowinandroid: 有跡象 跡象詞=[':app-nia-catalog:lintRelease', ':app:lintProdRelease', ':build-logic:convention:check', ':lint:lint', 'build', 'lint']
element-hq_element-x-android: 有跡象 跡象詞=[':app:lintFdroidDebug', ':app:lintGplayDebug', 'build', 'check', 'lint', 'lintDebug']
mozilla-mobile_firefox-android: 找不到(會印 A1) 跡象詞=[]
thunderbird_thunderbird-android: 有跡象 跡象詞=['build', 'lint']
```

判讀:前四個專案的 CI 確實跑 Android Lint(nowinandroid 的 `:app:lintProdRelease`、element-x 的 `:app:lintGplayDebug`、NewPipe 的 `lintContinuous`、thunderbird 的 `./gradlew lint`),判有跡象,對;architecture-samples 只跑 `:app:connectedCheck`(裝置測試,不帶 lint),判找不到,對;firefox-android 的 CI 在 Mozilla 的 Taskcluster,GitHub workflow 不跑 Gradle,判找不到、會多印一次 A1(計劃天花板 2)。
