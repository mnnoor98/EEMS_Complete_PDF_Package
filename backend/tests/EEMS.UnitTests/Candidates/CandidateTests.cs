using EEMS.Modules.Candidates.Domain;
namespace EEMS.UnitTests.Candidates;
public sealed class CandidateTests
{
    [Fact] public void CreateRequiresTenant()=>Assert.Throws<ArgumentException>(()=>Candidate.Create(Guid.Empty,"Candidate"));
    [Fact] public void AssignmentRequiresPositiveReferences()=>Assert.Throws<ArgumentOutOfRangeException>(()=>CandidateElection.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),0,1));
    [Fact] public void CreateNormalizesOptionalReference(){var candidate=Candidate.Create(Guid.NewGuid()," Candidate "," REF-1 ");Assert.Equal("Candidate",candidate.Name);Assert.Equal("REF-1",candidate.ExternalReference);}
}
