using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Geography.Domain;

public sealed class Area : Entity<long>
{
    private Area() { }
    private Area(long id, long? parentAreaId, short areaTypeId, string code, string nameBn, string? nameEn)
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(id);
        if (parentAreaId == id) throw new ArgumentException("An area cannot be its own parent.", nameof(parentAreaId));
        if (areaTypeId <= 0) throw new ArgumentOutOfRangeException(nameof(areaTypeId));
        Id=id; ParentAreaId=parentAreaId; AreaTypeId=areaTypeId; Code=Require(code,nameof(code),40).ToUpperInvariant();
        NameBn=Require(nameBn,nameof(nameBn),200); NameEn=Optional(nameEn,200); IsActive=true;
    }
    public long? ParentAreaId { get; private set; }
    public short AreaTypeId { get; private set; }
    public string Code { get; private set; } = string.Empty;
    public string NameBn { get; private set; } = string.Empty;
    public string? NameEn { get; private set; }
    public bool IsActive { get; private set; }
    public static Area Create(long id,long? parentAreaId,short areaTypeId,string code,string nameBn,string? nameEn=null) => new(id,parentAreaId,areaTypeId,code,nameBn,nameEn);
    private static string Require(string value,string parameter,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException($"{parameter} is invalid.",parameter);}
    private static string? Optional(string? value,int max){var text=value?.Trim();if(string.IsNullOrEmpty(text))return null;return text.Length<=max?text:throw new ArgumentException("Value is too long.");}
}
