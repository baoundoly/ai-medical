using AIMedical.Api.Models.DTOs;

namespace AIMedical.Api.Services;

public interface IAuthService
{
    Task<LoginResponse?> LoginAsync(string email, string password);
    Task<bool> RegisterAsync(string email, string password, string fullName, string role, int? tenantId);
    string GenerateRefreshToken();
}
