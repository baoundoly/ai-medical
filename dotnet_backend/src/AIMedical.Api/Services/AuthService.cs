using AIMedical.Api.Data;
using AIMedical.Api.Helpers;
using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Models.Entities;
using Microsoft.EntityFrameworkCore;
using System.Security.Cryptography;

namespace AIMedical.Api.Services;

public class AuthService : IAuthService
{
    private readonly AppDbContext _db;
    private readonly JwtHelper _jwt;

    public AuthService(AppDbContext db, JwtHelper jwt)
    {
        _db = db;
        _jwt = jwt;
    }

    public async Task<LoginResponse?> LoginAsync(string email, string password)
    {
        var user = await _db.Users
            .FirstOrDefaultAsync(u => u.Email == email.ToLower() && u.IsActive);

        if (user is null || !PasswordHelper.Verify(password, user.PasswordHash))
            return null;

        var accessToken = _jwt.CreateToken(user.Id, user.Email, user.Role.ToString(), user.TenantId);
        var refreshToken = GenerateRefreshToken();

        return new LoginResponse(accessToken, refreshToken, user.Role.ToString(), user.FullName);
    }

    public async Task<bool> RegisterAsync(
        string email, string password, string fullName, string role, int? tenantId)
    {
        var normalizedEmail = email.ToLower();
        var exists = await _db.Users.AnyAsync(u => u.Email == normalizedEmail);
        if (exists) return false;

        if (!Enum.TryParse<UserRole>(role, ignoreCase: true, out var userRole))
            userRole = UserRole.Patient;

        var user = new User
        {
            Email = normalizedEmail,
            PasswordHash = PasswordHelper.Hash(password),
            FullName = fullName,
            Role = userRole,
            TenantId = tenantId,
            IsActive = true,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        _db.Users.Add(user);
        await _db.SaveChangesAsync();
        return true;
    }

    public string GenerateRefreshToken()
    {
        var bytes = RandomNumberGenerator.GetBytes(64);
        return Convert.ToBase64String(bytes);
    }
}
