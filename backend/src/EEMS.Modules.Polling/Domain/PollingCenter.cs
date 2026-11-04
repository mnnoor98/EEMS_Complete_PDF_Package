using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Polling.Domain;
public sealed class PollingCenter:Entity<Guid>
{
    private PollingCenter(){}
    private PollingCenter(Guid id,long areaId,string code,string name,string? address){ArgumentOutOfRangeException.ThrowIfNegativeOrZero(areaId);Id=id;AreaId=areaId;Code=Require(code,50).ToUpperInvariant();Name=Require(name,250);Address=Optional(address,500);CreatedAtUtc=DateTimeOffset.UtcNow;}
    public long AreaId{get;private set;}public string Code{get;private set;}=string.Empty;public string Name{get;private set;}=string.Empty;public string? Address{get;private set;}public DateTimeOffset CreatedAtUtc{get;private set;}
    public static PollingCenter Create(long areaId,string code,string name,string? address=null)=>new(Guid.NewGuid(),areaId,code,name,address);
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
    private static string? Optional(string? value,int max){var text=value?.Trim();if(string.IsNullOrEmpty(text))return null;return text.Length<=max?text:throw new ArgumentException("Value is too long.");}
}
