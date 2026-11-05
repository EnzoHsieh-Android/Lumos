package bad

// case: drawable-context-view
data class HomeUiState(val icon: Drawable, val ctx: Context, val view: View)
// case: bitmap-nullable
data class PhotoState(val preview: Bitmap? = null)
