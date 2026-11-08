fun setupOne(webView: WebView) {
    webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW // BAD 常數
    webView.settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW) // BAD setter
}
fun setupTwo(webView: WebView, webSettings: WebSettings) {
    webView.settings.mixedContentMode = 0 // BAD 0 就是 MIXED_CONTENT_ALWAYS_ALLOW
    webSettings.mixedContentMode = 0 // BAD 接收者名字以 Settings 結尾
    webView.getSettings()!!.mixedContentMode = 0 // BAD getSettings()
    webView.settings.setMixedContentMode(0) // BAD setter 寫字面值
}
