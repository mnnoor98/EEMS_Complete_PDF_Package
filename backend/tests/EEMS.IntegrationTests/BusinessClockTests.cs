using EEMS.Api.Time;
using Microsoft.Extensions.Configuration;

namespace EEMS.IntegrationTests;

public sealed class BusinessClockTests
{
    [Fact]
    public void DhakaBusinessDateRollsOverBeforeUtcDate()
    {
        var utc=new DateTimeOffset(2026,11,4,19,0,0,TimeSpan.Zero);
        var configuration=new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string,string?>{{"Business:TimeZone","Asia/Dhaka"}}).Build();
        var clock=new BusinessClock(configuration,new FixedTimeProvider(utc));
        Assert.Equal(new DateOnly(2026,11,5),clock.Today);
        Assert.Equal(new DateTimeOffset(2026,11,4,18,0,0,TimeSpan.Zero),clock.StartOfTodayUtc);
    }

    private sealed class FixedTimeProvider(DateTimeOffset value):TimeProvider
    {
        public override DateTimeOffset GetUtcNow()=>value;
    }
}
