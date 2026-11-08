package good

@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun db(): AppDatabase
}

class Provider {
    fun db(ctx: Context) = EntryPointAccessors.fromApplication(ctx, AppEntryPoint::class.java)
}

@EntryPoint
@InstallIn(ActivityComponent::class)
interface ScreenEntryPoint {
    fun tracker(): Tracker
}

class Screen {
    fun tracker(activity: Activity) = EntryPointAccessors.fromActivity<ScreenEntryPoint>(activity)
}

// 容易誤報:entry point 宣告在別的檔,單檔看不到 @InstallIn,這條不報
class Elsewhere {
    fun get(ctx: Context) = EntryPointAccessors.fromApplication(ctx, OtherEntryPoint::class.java)
}
