using AIMedical.Api.Data;
using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Models.Entities;
using AIMedical.Api.Services;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace AIMedical.Tests;

public class PatientServiceTests
{
    private static AppDbContext CreateInMemoryDb(string dbName)
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(dbName)
            .Options;
        return new AppDbContext(options);
    }

    private static Tenant SeedTenant(AppDbContext db)
    {
        var tenant = new Tenant
        {
            Id = 1,
            Name = "Dhaka General Hospital",
            Code = "DGH",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };
        db.Tenants.Add(tenant);
        db.SaveChanges();
        return tenant;
    }

    [Fact]
    public async Task CreatePatient_GeneratesPatientUidInCorrectFormat()
    {
        await using var db = CreateInMemoryDb(nameof(CreatePatient_GeneratesPatientUidInCorrectFormat));
        SeedTenant(db);
        var service = new PatientService(db);

        var request = new PatientCreateRequest(
            "Fatima Begum", "01712345678", null,
            new DateTime(1990, 5, 15), "Female", "B+",
            "Dhaka", null, null);

        var result = await service.CreatePatientAsync(1, request);

        Assert.NotNull(result.PatientUid);
        // Expected format: {TenantCode}-{CityCode}-{Year}-{Seq:D6}
        // e.g. DGH-DGH-2024-000001
        var parts = result.PatientUid.Split('-');
        Assert.Equal(4, parts.Length);
        Assert.Equal("DGH", parts[0]);                            // TenantCode
        Assert.Equal(3, parts[1].Length);                         // CityCode (3 chars)
        Assert.Equal(DateTime.UtcNow.Year.ToString(), parts[2]);  // Year
        Assert.Equal(6, parts[3].Length);                         // Zero-padded seq
    }

    [Fact]
    public async Task CreatePatient_SequentialUidsIncrement()
    {
        await using var db = CreateInMemoryDb(nameof(CreatePatient_SequentialUidsIncrement));
        SeedTenant(db);
        var service = new PatientService(db);

        var req = new PatientCreateRequest(
            "Patient One", "01700000001", null, null, null, null, null, null, null);
        var req2 = new PatientCreateRequest(
            "Patient Two", "01700000002", null, null, null, null, null, null, null);

        var r1 = await service.CreatePatientAsync(1, req);
        var r2 = await service.CreatePatientAsync(1, req2);

        var seq1 = int.Parse(r1.PatientUid.Split('-')[3]);
        var seq2 = int.Parse(r2.PatientUid.Split('-')[3]);

        Assert.Equal(seq1 + 1, seq2);
    }

    [Fact]
    public async Task CheckDuplicates_FindsByMobile()
    {
        await using var db = CreateInMemoryDb(nameof(CheckDuplicates_FindsByMobile));
        SeedTenant(db);
        var service = new PatientService(db);

        await service.CreatePatientAsync(1,
            new PatientCreateRequest("Hassan Ali", "01888888888", null, null, null, null, null, null, null));

        var result = await service.CheckDuplicatesAsync(1,
            new DuplicateCheckRequest("Other Name", "01888888888", null));

        Assert.True(result.IsDuplicate);
        Assert.Single(result.Matches);
    }

    [Fact]
    public async Task CheckDuplicates_FindsByNameAndDob()
    {
        await using var db = CreateInMemoryDb(nameof(CheckDuplicates_FindsByNameAndDob));
        SeedTenant(db);
        var service = new PatientService(db);

        var dob = new DateTime(1985, 3, 10);
        await service.CreatePatientAsync(1,
            new PatientCreateRequest("Rahman Khan", null, null, dob, null, null, null, null, null));

        var result = await service.CheckDuplicatesAsync(1,
            new DuplicateCheckRequest("Rahman Khan", null, dob));

        Assert.True(result.IsDuplicate);
        Assert.Single(result.Matches);
    }

    [Fact]
    public async Task CheckDuplicates_NoDuplicate_ReturnsEmpty()
    {
        await using var db = CreateInMemoryDb(nameof(CheckDuplicates_NoDuplicate_ReturnsEmpty));
        SeedTenant(db);
        var service = new PatientService(db);

        var result = await service.CheckDuplicatesAsync(1,
            new DuplicateCheckRequest("Nobody", "01999999999", null));

        Assert.False(result.IsDuplicate);
        Assert.Empty(result.Matches);
    }

    [Fact]
    public async Task GetPatients_FiltersBySearch()
    {
        await using var db = CreateInMemoryDb(nameof(GetPatients_FiltersBySearch));
        SeedTenant(db);
        var service = new PatientService(db);

        await service.CreatePatientAsync(1,
            new PatientCreateRequest("Ayesha Siddiqua", "01600000001", null, null, null, null, null, null, null));
        await service.CreatePatientAsync(1,
            new PatientCreateRequest("Karim Uddin", "01600000002", null, null, null, null, null, null, null));

        var result = await service.GetPatientsAsync(1, 1, 20, "Ayesha");

        Assert.Single(result.Items);
        Assert.Equal("Ayesha Siddiqua", result.Items[0].Name);
    }
}
