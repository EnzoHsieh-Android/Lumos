package bad

@Composable
fun Bar(onClose: () -> Unit) {
    IconButton(onClick = onClose) {
        Icon(Icons.Default.Close, contentDescription = null) // BAD
    }
    FloatingActionButton(onClick = {}) { Icon(Icons.Default.Add, contentDescription = null) } // BAD
    Icon(
        Icons.Default.Share,
        contentDescription = null, // BAD
        modifier = Modifier.clickable { share() },
    )
}

// 代碼審 r2(規則A F8):徽章數字不是按鈕名稱,讀屏還是不知道按鈕做什麼
@Composable
fun Badged() {
    IconButton(onClick = {}) { BadgedBox(badge = { Text("3") }) { Icon(Icons.Default.Add, contentDescription = null) } } // BAD
}
