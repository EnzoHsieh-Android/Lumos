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
