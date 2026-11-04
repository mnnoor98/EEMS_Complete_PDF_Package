using EEMS.Modules.Candidates.Domain;
namespace EEMS.UnitTests.Candidates;
public sealed class CandidateTests
{
    [Fact] public void CreateRequiresTenant()=>Assert.Throws<ArgumentException>(()=>Candidate.Create(Guid.Empty,"Candidate"));
    [Fact] public void AssignmentRequiresPositiveReferences()=>Assert.Throws<ArgumentOutOfRangeException>(()=>CandidateElection.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),0,1));
}
