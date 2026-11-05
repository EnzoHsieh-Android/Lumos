package good

// case: res-id
data class HomeUiState2(@DrawableRes val iconRes: Int, val title: String)
// case: non-state-holder-with-view
class ViewHolderArgs(val view: View)
// case: state-with-viewmodel-name
data class PageState(val viewMode: ViewMode, val reviewCount: Int)
