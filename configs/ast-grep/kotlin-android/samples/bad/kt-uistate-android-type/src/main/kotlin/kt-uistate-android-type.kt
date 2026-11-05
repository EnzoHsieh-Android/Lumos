package bad

// case: drawable-context-view
data class HomeUiState(val icon: Drawable, val ctx: Context, val view: View)
// case: bitmap-nullable
data class PhotoState(val preview: Bitmap? = null)

// case: sealed-state-nested(代碼審 r2 規則A F3:外層 sealed *State,巢狀 data class 夾 Context)
sealed class LoginState { data class Done(val ctx: Context) : LoginState() }
