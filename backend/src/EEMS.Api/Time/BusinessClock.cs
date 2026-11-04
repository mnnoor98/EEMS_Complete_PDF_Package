namespace EEMS.Api.Time;

public interface IBusinessClock
{
    DateTimeOffset UtcNow { get; }
    DateOnly Today { get; }
    DateTimeOffset StartOfTodayUtc { get; }
}

public sealed class BusinessClock(IConfiguration configuration,TimeProvider timeProvider):IBusinessClock
{
    private readonly TimeZoneInfo zone=TimeZoneInfo.FindSystemTimeZoneById(configuration["Business:TimeZone"]??"Asia/Dhaka");
    public DateTimeOffset UtcNow=>timeProvider.GetUtcNow();
    public DateOnly Today=>DateOnly.FromDateTime(TimeZoneInfo.ConvertTime(UtcNow,zone).DateTime);
    public DateTimeOffset StartOfTodayUtc
    {
        get
        {
            var local=TimeZoneInfo.ConvertTime(UtcNow,zone);
            var localStart=new DateTime(local.Year,local.Month,local.Day,0,0,0,DateTimeKind.Unspecified);
            return new DateTimeOffset(TimeZoneInfo.ConvertTimeToUtc(localStart,zone),TimeSpan.Zero);
        }
    }
}
