fun enableStandard() {
    WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG) // GOOD 標準寫法:直接傳除錯旗標
}
fun enableInDebug() {
    if (BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) } // GOOD
    if (BuildConfig.DEBUG) WebView.setWebContentsDebuggingEnabled(true) // GOOD 不帶大括號
    when { BuildConfig.DEBUG -> WebView.setWebContentsDebuggingEnabled(true) } // GOOD when 分支
    if (BuildConfig.DEBUG) { if (Build.VERSION.SDK_INT >= 19) { WebView.setWebContentsDebuggingEnabled(true) } } // GOOD 外層是 DEBUG
    WebView.setWebContentsDebuggingEnabled(false) // GOOD
}
