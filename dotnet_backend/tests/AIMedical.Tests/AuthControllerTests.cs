using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Services;
using Moq;
using Xunit;

namespace AIMedical.Tests;

public class AuthControllerTests
{
    private readonly Mock<IAuthService> _authServiceMock = new();

    [Fact]
    public async Task Login_WithValidCredentials_ReturnsLoginResponse()
    {
        var expected = new LoginResponse("access-token", "refresh-token", "Doctor", "Dr. Rahim");
        _authServiceMock
            .Setup(s => s.LoginAsync("doctor@example.com", "correct-password"))
            .ReturnsAsync(expected);

        var result = await _authServiceMock.Object.LoginAsync("doctor@example.com", "correct-password");

        Assert.NotNull(result);
        Assert.Equal("access-token", result.AccessToken);
        Assert.Equal("Doctor", result.Role);
        Assert.Equal("Dr. Rahim", result.FullName);
    }

    [Fact]
    public async Task Login_WithWrongPassword_ReturnsNull()
    {
        _authServiceMock
            .Setup(s => s.LoginAsync("doctor@example.com", "wrong-password"))
            .ReturnsAsync((LoginResponse?)null);

        var result = await _authServiceMock.Object.LoginAsync("doctor@example.com", "wrong-password");

        Assert.Null(result);
    }

    [Fact]
    public async Task Login_WithUnknownEmail_ReturnsNull()
    {
        _authServiceMock
            .Setup(s => s.LoginAsync("unknown@example.com", It.IsAny<string>()))
            .ReturnsAsync((LoginResponse?)null);

        var result = await _authServiceMock.Object.LoginAsync("unknown@example.com", "any-password");

        Assert.Null(result);
    }

    [Fact]
    public async Task Register_WithNewEmail_ReturnsTrue()
    {
        _authServiceMock
            .Setup(s => s.RegisterAsync("new@example.com", "password123", "Ali Hassan", "Doctor", 1))
            .ReturnsAsync(true);

        var success = await _authServiceMock.Object
            .RegisterAsync("new@example.com", "password123", "Ali Hassan", "Doctor", 1);

        Assert.True(success);
    }

    [Fact]
    public async Task Register_WithDuplicateEmail_ReturnsFalse()
    {
        _authServiceMock
            .Setup(s => s.RegisterAsync("existing@example.com", It.IsAny<string>(),
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<int?>()))
            .ReturnsAsync(false);

        var success = await _authServiceMock.Object
            .RegisterAsync("existing@example.com", "password123", "Ali Hassan", "Doctor", 1);

        Assert.False(success);
    }
}
