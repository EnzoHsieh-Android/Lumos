package good

@Composable
fun Bar(onClose: () -> Unit) {
    IconButton(onClick = onClose) {
        Icon(Icons.Default.Close, contentDescription = stringResource(R.string.close))
    }
    Row(Modifier.clickable(onClickLabel = "x", role = Role.Button) { open() }) {
        Icon(Icons.Default.Star, contentDescription = null)
        Text(stringResource(R.string.fav))
    }
    Image(painterResource(R.drawable.bg), contentDescription = null)
}

// 容易誤報(代碼審 r1 m4):圖示旁有文字標籤,讀屏念的是文字
@Composable
fun AddButton() {
    IconButton(onClick = {}) {
        Row { Icon(Icons.Default.Add, contentDescription = null); Text("Add") }
    }
}
