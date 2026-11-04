using System.Reflection;

namespace EEMS.ArchitectureTests;

public sealed class ModuleBoundaryTests
{
    [Fact]
    public void DomainModulesDoNotReferenceApiHost()
    {
        var apiAssembly = typeof(Program).Assembly;
        var moduleAssemblies = apiAssembly
            .GetReferencedAssemblies()
            .Where(reference => reference.Name?.StartsWith("EEMS.Modules.", StringComparison.Ordinal) == true)
            .Select(Assembly.Load)
            .ToArray();

        Assert.NotEmpty(moduleAssemblies);

        var offenders = moduleAssemblies
            .Where(assembly => assembly.GetReferencedAssemblies().Any(reference => reference.Name == "EEMS.Api"))
            .Select(assembly => assembly.GetName().Name)
            .OrderBy(name => name)
            .ToArray();

        Assert.True(
            offenders.Length == 0,
            $"Domain modules must not depend on the API host. Offenders: {string.Join(", ", offenders)}");
    }
}
