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

// 容易誤報(代碼審 r1 M8):預覽裡手建假的或帶假資料的 ViewModel,不經 DI 不會崩
@Preview
@Composable
private fun FakePreview() {
    HomeScreen(vm = FakeHomeViewModel())
}

@Preview(showBackground = true)
@Composable
private fun CartPreview() {
    AppTheme { Cart(CartViewModel(FakeRepo())) }
}
