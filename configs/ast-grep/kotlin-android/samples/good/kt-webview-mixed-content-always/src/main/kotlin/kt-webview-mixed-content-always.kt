fun setupOne(webView: WebView) {
    webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW // GOOD 建議值
    webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE // GOOD 相容模式
}
fun setupTwo(webView: WebView, cfg: PlayerConfig) {
    cfg.mixedContentMode = 0 // GOOD 接收者不是 WebView 設定
    webView.settings.setMixedContentMode(resolve(0, 1)) // GOOD 0 是內層呼叫的參數
}
fun setupThree(webView: WebView) {
    if (BuildConfig.DEBUG) { webView.settings.mixedContentMode = 0 } // GOOD 只在除錯版
}
