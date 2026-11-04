using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Elections.Domain;

public sealed class ElectionType : Entity<short>
{
    private ElectionType() { }
    private ElectionType(short id,string code,string name){if(id<=0)throw new ArgumentOutOfRangeException(nameof(id));Id=id;Code=Require(code,40).ToUpperInvariant();Name=Require(name,120);IsActive=true;}
    public string Code{get;private set;}=string.Empty; public string Name{get;private set;}=string.Empty; public bool IsActive{get;private set;}
    public static ElectionType Create(short id,string code,string name)=>new(id,code,name);
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
}
