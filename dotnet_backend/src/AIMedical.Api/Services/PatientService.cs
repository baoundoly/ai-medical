using AIMedical.Api.Data;
using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Models.Entities;
using Microsoft.EntityFrameworkCore;

namespace AIMedical.Api.Services;

public class PatientService : IPatientService
{
    private readonly AppDbContext _db;

    public PatientService(AppDbContext db)
    {
        _db = db;
    }

    public async Task<PatientResponse> CreatePatientAsync(int tenantId, PatientCreateRequest request)
    {
        var tenant = await _db.Tenants.FindAsync(tenantId)
            ?? throw new InvalidOperationException($"Tenant {tenantId} not found.");

        var uid = await GeneratePatientUidAsync(tenant);

        var patient = new Patient
        {
            TenantId = tenantId,
            PatientUid = uid,
            Name = request.Name,
            Mobile = request.Mobile,
            Nid = request.Nid,
            DateOfBirth = request.DateOfBirth,
            Gender = request.Gender,
            BloodGroup = request.BloodGroup,
            Address = request.Address,
            EmergencyContactName = request.EmergencyContactName,
            EmergencyContactPhone = request.EmergencyContactPhone,
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };

        _db.Patients.Add(patient);
        await _db.SaveChangesAsync();

        return MapToResponse(patient);
    }

    public async Task<PagedResponse<PatientResponse>> GetPatientsAsync(
        int tenantId, int page, int pageSize, string? search)
    {
        var query = _db.Patients
            .Where(p => p.TenantId == tenantId && p.IsActive);

        if (!string.IsNullOrWhiteSpace(search))
        {
            var term = search.Trim().ToLower();
            query = query.Where(p =>
                p.Name.ToLower().Contains(term) ||
                (p.Mobile != null && p.Mobile.Contains(term)) ||
                p.PatientUid.ToLower().Contains(term));
        }

        var total = await query.CountAsync();
        var items = await query
            .OrderByDescending(p => p.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(p => MapToResponse(p))
            .ToListAsync();

        return new PagedResponse<PatientResponse>(items, total, page, pageSize);
    }

    public async Task<PatientResponse?> GetPatientByIdAsync(int tenantId, int id)
    {
        var patient = await _db.Patients
            .FirstOrDefaultAsync(p => p.Id == id && p.TenantId == tenantId && p.IsActive);
        return patient is null ? null : MapToResponse(patient);
    }

    public async Task<PatientResponse?> UpdatePatientAsync(
        int tenantId, int id, PatientUpdateRequest request)
    {
        var patient = await _db.Patients
            .FirstOrDefaultAsync(p => p.Id == id && p.TenantId == tenantId && p.IsActive);

        if (patient is null) return null;

        if (request.Name is not null) patient.Name = request.Name;
        if (request.Mobile is not null) patient.Mobile = request.Mobile;
        if (request.Nid is not null) patient.Nid = request.Nid;
        if (request.DateOfBirth.HasValue) patient.DateOfBirth = request.DateOfBirth;
        if (request.Gender is not null) patient.Gender = request.Gender;
        if (request.BloodGroup is not null) patient.BloodGroup = request.BloodGroup;
        if (request.Address is not null) patient.Address = request.Address;
        if (request.EmergencyContactName is not null) patient.EmergencyContactName = request.EmergencyContactName;
        if (request.EmergencyContactPhone is not null) patient.EmergencyContactPhone = request.EmergencyContactPhone;

        await _db.SaveChangesAsync();
        return MapToResponse(patient);
    }

    public async Task<DuplicateCheckResponse> CheckDuplicatesAsync(
        int tenantId, DuplicateCheckRequest request)
    {
        var query = _db.Patients
            .Where(p => p.TenantId == tenantId && p.IsActive);

        // Match by mobile OR (name + DOB)
        query = query.Where(p =>
            (request.Mobile != null && p.Mobile == request.Mobile) ||
            (p.Name.ToLower() == request.Name.ToLower() &&
             request.DateOfBirth.HasValue &&
             p.DateOfBirth == request.DateOfBirth));

        var matches = await query
            .Select(p => MapToResponse(p))
            .ToListAsync();

        return new DuplicateCheckResponse(matches.Count > 0, matches);
    }

    private async Task<string> GeneratePatientUidAsync(Tenant tenant)
    {
        var year = DateTime.UtcNow.Year;
        // Count existing patients for this tenant in the current year to get sequence
        var count = await _db.Patients
            .CountAsync(p => p.TenantId == tenant.Id &&
                             p.CreatedAt.Year == year);
        var seq = count + 1;

        // CityCode derived from first 3 chars of tenant Code
        var cityCode = tenant.Code.Length >= 3
            ? tenant.Code[..3].ToUpper()
            : tenant.Code.ToUpper().PadRight(3, 'X');

        return $"{tenant.Code}-{cityCode}-{year}-{seq:D6}";
    }

    private static PatientResponse MapToResponse(Patient p) => new(
        p.Id, p.PatientUid, p.Name, p.Mobile, p.Gender, p.BloodGroup, p.CreatedAt);
}
