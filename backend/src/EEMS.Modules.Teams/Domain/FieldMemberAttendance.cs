using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Teams.Domain;
public sealed class FieldMemberAttendance:Entity<Guid>
{
    private FieldMemberAttendance(){}
    private FieldMemberAttendance(Guid id,Guid tenantId,Guid teamId,Guid memberId,DateOnly date,string status,Guid recordedByUserId,string? note){if(tenantId==Guid.Empty||teamId==Guid.Empty||memberId==Guid.Empty||recordedByUserId==Guid.Empty)throw new ArgumentException("Attendance references are required.");Id=id;TenantId=tenantId;TeamId=teamId;MemberId=memberId;AttendanceDate=date;Status=Required(status,20);RecordedByUserId=recordedByUserId;Note=Optional(note,300);RecordedAtUtc=DateTimeOffset.UtcNow;}
    public Guid TenantId{get;private set;}public Guid TeamId{get;private set;}public Guid MemberId{get;private set;}public DateOnly AttendanceDate{get;private set;}public string Status{get;private set;}=string.Empty;public Guid RecordedByUserId{get;private set;}public string? Note{get;private set;}public DateTimeOffset RecordedAtUtc{get;private set;}
    public static FieldMemberAttendance Record(Guid tenantId,Guid teamId,Guid memberId,DateOnly date,string status,Guid recordedByUserId,string? note)=>new(Guid.NewGuid(),tenantId,teamId,memberId,date,status,recordedByUserId,note);
    private static string Required(string value,int max){var x=value?.Trim().ToUpperInvariant()??"";return x.Length is >0&&x.Length<=max?x:throw new ArgumentException("Value is invalid.");}private static string? Optional(string? value,int max){var x=value?.Trim();return string.IsNullOrWhiteSpace(x)?null:x.Length<=max?x:throw new ArgumentException("Value is invalid.");}
}
