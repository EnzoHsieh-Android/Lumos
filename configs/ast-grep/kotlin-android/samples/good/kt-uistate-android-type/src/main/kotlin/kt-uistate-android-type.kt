package good

// case: res-id
data class HomeUiState2(@DrawableRes val iconRes: Int, val title: String)
// case: non-state-holder-with-view
class ViewHolderArgs(val view: View)
// case: state-with-viewmodel-name
data class PageState(val viewMode: ViewMode, val reviewCount: Int)

// case: compose-state-holder(代碼審 r1 M9:官方 state holder 範例,不是 ViewModel 輸出的 UiState)
class MyAppState(val navController: NavHostController, private val resources: Resources, val ctx: Context)
