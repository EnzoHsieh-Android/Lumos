package bad

@Preview // BAD
@Composable
private fun ButtonPreview() {
    PrimaryButton("OK", onClick = {})
}

@Preview(name = "dark", uiMode = 32) // BAD
@Composable
private fun CardPreview() { Card { Text("a") } }
