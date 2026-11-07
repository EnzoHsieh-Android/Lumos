fun setupOne(webView: WebView) {
    webView.settings.allowUniversalAccessFromFileURLs = false // GOOD 明寫 false
    webView.settings.setAllowFileAccessFromFileURLs(false) // GOOD
}
fun setupTwo(webView: WebView, ctx: Context) {
    // GOOD 本機內容用 WebViewAssetLoader 走 https 網址載入,不開檔案網址存取
    val loader = WebViewAssetLoader.Builder()
        .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(ctx))
        .build()
    webView.settings.allowFileAccess = true // GOOD 只是一般檔案存取,不是跨來源(MASTG-TEST-0252 不算漏洞)
    webView.loadUrl("https://appassets.androidplatform.net/assets/index.html")
}
fun setupThree(webView: WebView) {
    if (BuildConfig.DEBUG) { webView.settings.allowFileAccessFromFileURLs = true } // GOOD 只在除錯版開
}
