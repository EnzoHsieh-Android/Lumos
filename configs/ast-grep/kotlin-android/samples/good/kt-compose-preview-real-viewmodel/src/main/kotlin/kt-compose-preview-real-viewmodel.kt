package good

@Preview
@Composable
private fun ScreenPreview() {
    AppTheme { ScreenContent(state = UiState(items = listOf())) }
}

@Composable
fun ScreenRoute(vm: CartViewModel = hiltViewModel()) {
    ScreenContent(vm.state)
}
