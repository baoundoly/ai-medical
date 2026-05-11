namespace AIMedical.Api.Helpers;

public static class PasswordHelper
{
    public static string Hash(string plainPassword)
        => BCrypt.Net.BCrypt.HashPassword(plainPassword, workFactor: 12);

    public static bool Verify(string plainPassword, string hash)
        => BCrypt.Net.BCrypt.Verify(plainPassword, hash);
}
