fun enableAlways() {
    WebView.setWebContentsDebuggingEnabled(true) // BAD 完全沒包
}
fun enableWrongBranch(flavorDebug: Boolean) {
    if (!BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) } // BAD 否定
    if (BuildConfig.DEBUG) { } else { android.webkit.WebView.setWebContentsDebuggingEnabled(true) } // BAD else 分支
    if (Build.VERSION.SDK_INT >= 19) { WebView.setWebContentsDebuggingEnabled(true) } // BAD 只包版本判斷
    if (BuildConfig.DEBUG || flavorDebug) { WebView.setWebContentsDebuggingEnabled(true) } // BAD || 連別的條件
}
