using Microsoft.AspNetCore.Authorization;

namespace EEMS.Modules.Identity.Security;

public sealed record PermissionRequirement(string PermissionCode) : IAuthorizationRequirement;
