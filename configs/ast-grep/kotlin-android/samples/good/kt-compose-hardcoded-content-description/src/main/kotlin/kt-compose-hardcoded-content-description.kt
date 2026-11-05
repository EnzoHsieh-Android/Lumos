package good

@Composable
fun Bar() {
    Icon(Icons.Default.Close, contentDescription = stringResource(R.string.close))
    Image(p, contentDescription = null)
    Box(Modifier.semantics { contentDescription = label })
    Text("關閉")
}
