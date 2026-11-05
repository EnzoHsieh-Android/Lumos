// 語意覆核級已知誤報:Compose MutableState 在主執行緒的尾隨 lambda 裡讀改寫,形狀分不出它不是 StateFlow
@Composable
fun Tap(count: MutableState<Int>) {
    Box(Modifier.clickable { count.value = count.value + 1 })
    Box(Modifier.pointerInput(Unit) { detectTapGestures { count.value = count.value + 1 } })
}
