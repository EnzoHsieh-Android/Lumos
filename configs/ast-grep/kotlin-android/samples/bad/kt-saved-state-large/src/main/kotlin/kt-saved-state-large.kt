package bad

// case: handle-arraylist
fun T1ViewModel.keep(list: List<Item>) { savedStateHandle["list"] = ArrayList(list) }
// case: bundle-bitmap
fun T2Activity.save(outState: Bundle) { outState.putParcelable("bmp", bitmap) }
// case: parcelable-arraylist
fun T3Fragment.save(outState: Bundle) { outState.putParcelableArrayList("items", items) }
