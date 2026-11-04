using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Polling.Domain;
public sealed class Booth:Entity<Guid>
{
    private Booth(){} private Booth(Guid id,Guid centerId,string code,string name){if(centerId==Guid.Empty)throw new ArgumentException("Center is required.",nameof(centerId));Id=id;CenterId=centerId;Code=Require(code,50).ToUpperInvariant();Name=Require(name,120);IsActive=true;}
    public Guid CenterId{get;private set;}public string Code{get;private set;}=string.Empty;public string Name{get;private set;}=string.Empty;public bool IsActive{get;private set;}
    public static Booth Create(Guid centerId,string code,string name)=>new(Guid.NewGuid(),centerId,code,name);
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
}
