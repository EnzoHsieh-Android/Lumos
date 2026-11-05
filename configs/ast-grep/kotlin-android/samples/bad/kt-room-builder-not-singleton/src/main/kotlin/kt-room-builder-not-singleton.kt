class MainActivity : AppCompatActivity() {
    override fun onCreate(b: Bundle?) {
        val db = Room.databaseBuilder(this, AppDb::class.java, "app.db").build() // BAD
    }
}
fun loadUsers(ctx: Context) = Room.databaseBuilder<AppDb>(ctx, "app.db").build().userDao() // BAD
