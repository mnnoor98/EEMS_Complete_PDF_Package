using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Elections.Domain;

public sealed class Position : Entity<long>
{
    private Position() { }
    private Position(long id,short electionTypeId,string code,string name){ArgumentOutOfRangeException.ThrowIfNegativeOrZero(id);if(electionTypeId<=0)throw new ArgumentOutOfRangeException(nameof(electionTypeId));Id=id;ElectionTypeId=electionTypeId;Code=Require(code,60).ToUpperInvariant();Name=Require(name,120);IsActive=true;}
    public short ElectionTypeId{get;private set;} public string Code{get;private set;}=string.Empty; public string Name{get;private set;}=string.Empty; public bool IsActive{get;private set;}
    public static Position Create(long id,short electionTypeId,string code,string name)=>new(id,electionTypeId,code,name);
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
}
