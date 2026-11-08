package bad

@EntryPoint
@InstallIn(ActivityComponent::class)
interface ScreenEntryPoint {
    fun tracker(): Tracker
}

@EntryPoint
@InstallIn(SingletonComponent::class)
interface AppEntryPoint {
    fun db(): AppDatabase
}

class Widget {
    fun tracker(ctx: Context) = EntryPointAccessors.fromApplication(ctx, ScreenEntryPoint::class.java)  // BAD
    fun db(activity: Activity) = EntryPointAccessors.fromActivity<AppEntryPoint>(activity)  // BAD
}
