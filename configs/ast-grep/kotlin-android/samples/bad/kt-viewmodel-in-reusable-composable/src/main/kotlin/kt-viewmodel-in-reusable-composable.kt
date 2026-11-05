package bad

// case: list-item-hiltViewModel
@Composable
fun UserRow(user: User) {
    val vm: RowViewModel = hiltViewModel()
    Text(user.name)
}
// case: card-viewModel-generic
@Composable
fun PriceCard(id: String) {
    val vm = viewModel<PriceViewModel>()
}
