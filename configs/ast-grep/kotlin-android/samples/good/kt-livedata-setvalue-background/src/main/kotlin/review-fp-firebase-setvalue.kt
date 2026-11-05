// 語意覆核級已知誤報:Firebase DatabaseReference.setValue 可在任意執行緒呼叫,形狀分不出它不是 LiveData
fun save(scope: CoroutineScope, dbRef: DatabaseReference, x: Any) {
    scope.launch(Dispatchers.IO) { dbRef.child("a").setValue(x).await() }
}
suspend fun prefsWrite(prefs: Prefs, a: String, b: String) {
    withContext(Dispatchers.IO) { prefs.setValue(a, b) }
}
