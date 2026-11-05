package bad

// case: save-persistable
class V1Activity : AppCompatActivity() {
    override fun onSaveInstanceState(outState: Bundle, outPersistentState: PersistableBundle) { super.onSaveInstanceState(outState, outPersistentState) }
}
// case: oncreate-persistable-nullable
class V2Activity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?, persistentState: PersistableBundle?) { super.onCreate(savedInstanceState, persistentState) }
}
