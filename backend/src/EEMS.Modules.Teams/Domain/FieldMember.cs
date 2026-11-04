using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Teams.Domain;
public sealed class FieldMember:Entity<Guid>
{
    private FieldMember(){}
    private FieldMember(Guid id,Guid tenantId,Guid teamId,string fullName,string phone,string memberType,long? areaId,string? address,string? emergencyContact)
    {if(tenantId==Guid.Empty||teamId==Guid.Empty)throw new ArgumentException("Tenant and team are required.");Id=id;TenantId=tenantId;TeamId=teamId;FullName=Text(fullName,200,true)!;Phone=Text(phone,30,true)!;MemberType=Text(memberType,80,true)!;AreaId=areaId;Address=Text(address,500,false);EmergencyContact=Text(emergencyContact,120,false);JoinedAtUtc=DateTimeOffset.UtcNow;IsActive=true;}
    public Guid TenantId{get;private set;}public Guid TeamId{get;private set;}public string FullName{get;private set;}=string.Empty;public string Phone{get;private set;}=string.Empty;public string MemberType{get;private set;}=string.Empty;public long? AreaId{get;private set;}public string? Address{get;private set;}public string? EmergencyContact{get;private set;}public DateTimeOffset JoinedAtUtc{get;private set;}public bool IsActive{get;private set;}
    public static FieldMember Create(Guid tenantId,Guid teamId,string fullName,string phone,string memberType,long? areaId,string? address,string? emergencyContact)=>new(Guid.NewGuid(),tenantId,teamId,fullName,phone,memberType,areaId,address,emergencyContact);
    private static string? Text(string? value,int max,bool required){var text=value?.Trim();if(required&&string.IsNullOrWhiteSpace(text)||text?.Length>max)throw new ArgumentException("Value is invalid.");return string.IsNullOrWhiteSpace(text)?null:text;}
}
