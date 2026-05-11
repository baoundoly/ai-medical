using AIMedical.Api.Models.DTOs;

namespace AIMedical.Api.Services;

public interface IPatientService
{
    Task<PatientResponse> CreatePatientAsync(int tenantId, PatientCreateRequest request);
    Task<PagedResponse<PatientResponse>> GetPatientsAsync(int tenantId, int page, int pageSize, string? search);
    Task<PatientResponse?> GetPatientByIdAsync(int tenantId, int id);
    Task<PatientResponse?> UpdatePatientAsync(int tenantId, int id, PatientUpdateRequest request);
    Task<DuplicateCheckResponse> CheckDuplicatesAsync(int tenantId, DuplicateCheckRequest request);
}
