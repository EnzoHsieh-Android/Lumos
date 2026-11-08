fun setupOne(webView: WebView) {
    webView.settings.allowFileAccess = true // BAD 屬性賦值
    webView.settings.setAllowFileAccess(true) // BAD setter
}
fun setupTwo(s: WebSettings?) {
    s?.setAllowFileAccess(true) // BAD 安全呼叫
}
