package bad

@Preview
@Composable
private fun ScreenPreview() {
    AppTheme { Screen(viewModel()) } // BAD
}

@PreviewLightDark
@Composable
private fun DetailPreview() {
    AppTheme { Detail(vm = hiltViewModel()) } // BAD
}

@Preview(showBackground = true)
@Composable
private fun CartPreview() {
    AppTheme { Cart(CartViewModel(FakeRepo())) } // BAD
}
