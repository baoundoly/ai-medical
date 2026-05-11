using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly IAuthService _auth;

    public AuthController(IAuthService auth)
    {
        _auth = auth;
    }

    /// <summary>Authenticate and receive JWT tokens.</summary>
    [AllowAnonymous]
    [HttpPost("login")]
    public async Task<ActionResult<LoginResponse>> Login([FromBody] LoginRequest request)
    {
        var result = await _auth.LoginAsync(request.Email, request.Password);
        if (result is null)
            return Unauthorized(new { message = "Invalid email or password." });

        return Ok(result);
    }

    /// <summary>Register a new user account.</summary>
    [AllowAnonymous]
    [HttpPost("register")]
    public async Task<IActionResult> Register([FromBody] RegisterRequest request)
    {
        var success = await _auth.RegisterAsync(
            request.Email, request.Password, request.FullName, request.Role, request.TenantId);

        if (!success)
            return Conflict(new { message = "Email already registered." });

        return StatusCode(201, new { message = "User registered successfully." });
    }

    /// <summary>Refresh access token using a refresh token.</summary>
    [AllowAnonymous]
    [HttpPost("refresh")]
    public IActionResult Refresh([FromBody] RefreshTokenRequest request)
    {
        // In a production system, refresh tokens are persisted and validated.
        // This stub returns a 501 to indicate it is not yet implemented.
        return StatusCode(501, new { message = "Refresh token persistence not yet implemented." });
    }
}
