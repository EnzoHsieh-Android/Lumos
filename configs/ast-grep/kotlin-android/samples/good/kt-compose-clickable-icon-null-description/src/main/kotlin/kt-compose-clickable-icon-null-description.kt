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
