using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Teams.Domain;
public sealed class MemberWorkAssignment:Entity<Guid>
{
    private MemberWorkAssignment(){}
    private MemberWorkAssignment(Guid id,Guid tenantId,Guid electionId,Guid teamId,Guid memberId,short stateId,short priorityId,string title,string? instructions,DateTimeOffset? dueAtUtc)
    {if(tenantId==Guid.Empty||electionId==Guid.Empty||teamId==Guid.Empty||memberId==Guid.Empty)throw new ArgumentException("Assignment references are required.");if(stateId<=0||priorityId<=0)throw new ArgumentOutOfRangeException(nameof(stateId));Id=id;TenantId=tenantId;ElectionId=electionId;TeamId=teamId;MemberId=memberId;StateId=stateId;PriorityId=priorityId;Title=Text(title,200,true)!;Instructions=Text(instructions,1000,false);DueAtUtc=dueAtUtc;CreatedAtUtc=DateTimeOffset.UtcNow;Version=1;}
    public Guid TenantId{get;private set;}public Guid ElectionId{get;private set;}public Guid TeamId{get;private set;}public Guid MemberId{get;private set;}public short StateId{get;private set;}public short PriorityId{get;private set;}public string Title{get;private set;}=string.Empty;public string? Instructions{get;private set;}public DateTimeOffset? DueAtUtc{get;private set;}public DateTimeOffset CreatedAtUtc{get;private set;}public Guid? VerifiedByUserId{get;private set;}public DateTimeOffset? VerifiedAtUtc{get;private set;}public string? VerificationNote{get;private set;}public int Version{get;private set;}
    public static MemberWorkAssignment Create(Guid tenantId,Guid electionId,Guid teamId,Guid memberId,short stateId,short priorityId,string title,string? instructions,DateTimeOffset? dueAtUtc)=>new(Guid.NewGuid(),tenantId,electionId,teamId,memberId,stateId,priorityId,title,instructions,dueAtUtc);
    public void MoveTo(short stateId){if(stateId<=0)throw new ArgumentOutOfRangeException(nameof(stateId));StateId=stateId;Version++;}
    public void Verify(Guid userId,string? note){if(userId==Guid.Empty)throw new ArgumentException("Verifier is required.");VerifiedByUserId=userId;VerifiedAtUtc=DateTimeOffset.UtcNow;VerificationNote=Text(note,500,false);Version++;}
    private static string? Text(string? value,int max,bool required){var text=value?.Trim();if(required&&string.IsNullOrWhiteSpace(text)||text?.Length>max)throw new ArgumentException("Value is invalid.");return string.IsNullOrWhiteSpace(text)?null:text;}
}
