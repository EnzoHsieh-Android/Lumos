sealed class ScopedResource : IDisposable
{
    private bool _disposed;
    public int Read() => _disposed ? throw new ObjectDisposedException(nameof(ScopedResource)) : 42;
    public void Dispose() => _disposed = true;
}

static class Program
{
    static int Main(string[] args)
    {
        if (args.SingleOrDefault() == "normal")
        {
            using var live = new ScopedResource();
            return live.Read() == 42 ? 0 : 3;
        }

        Func<int> queuedWork = () =>
        {
            using var ownScope = new ScopedResource();
            return ownScope.Read();
        };
        return queuedWork() == 42 ? 0 : 2;
    }
}
