package good

@Preview
@Composable
private fun ButtonPreview() {
    AppTheme { PrimaryButton("OK", onClick = {}) }
}

@Preview
@Composable
private fun CardPreview() {
    MaterialTheme(colorScheme = darkColorScheme()) { Card { Text("a") } }
}

@Composable
fun NotAPreview() { Text("x") }
