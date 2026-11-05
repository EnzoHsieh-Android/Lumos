package good

// case: handle-id
fun T4ViewModel.keep(id: String) { savedStateHandle["id"] = id }
// case: bundle-string
fun T5Activity.save(outState: Bundle) { outState.putString("query", q) }
// case: bundle-small-parcelable
fun T6Activity.save(outState: Bundle) { outState.putParcelable("scroll", layoutManager.onSaveInstanceState()) }
