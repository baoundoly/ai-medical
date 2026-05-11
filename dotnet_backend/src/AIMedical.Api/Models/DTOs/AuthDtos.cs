using System.ComponentModel.DataAnnotations;

namespace AIMedical.Api.Models.DTOs;

public record LoginRequest(
    [Required][EmailAddress] string Email,
    [Required] string Password
);

public record LoginResponse(
    string AccessToken,
    string RefreshToken,
    string Role,
    string FullName
);

public record RegisterRequest(
    [Required][EmailAddress] string Email,
    [Required][MinLength(8)] string Password,
    [Required] string FullName,
    [Required] string Role,
    int? TenantId
);

public record RefreshTokenRequest([Required] string RefreshToken);
