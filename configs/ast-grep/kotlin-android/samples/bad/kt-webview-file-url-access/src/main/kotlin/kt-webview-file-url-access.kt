fun setupOne(webView: WebView) {
    webView.settings.allowUniversalAccessFromFileURLs = true // BAD 多層接收者的屬性賦值
    webView.settings.setAllowFileAccessFromFileURLs(true) // BAD setter
}
fun setupTwo(webView: WebView, s: WebSettings?) {
    webView.settings.apply { allowFileAccessFromFileURLs = true } // BAD apply 裡不帶接收者
    with(webView.settings) { setAllowUniversalAccessFromFileURLs(true) } // BAD with 裡不帶接收者
    s?.setAllowUniversalAccessFromFileURLs(true) // BAD 安全呼叫
}
