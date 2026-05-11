using System.ComponentModel.DataAnnotations;

namespace AIMedical.Api.Models.DTOs;

public record PatientCreateRequest(
    [Required] string Name,
    [Phone] string? Mobile,
    string? Nid,
    DateTime? DateOfBirth,
    string? Gender,
    string? BloodGroup,
    string? Address,
    string? EmergencyContactName,
    string? EmergencyContactPhone
);

public record PatientUpdateRequest(
    string? Name,
    [Phone] string? Mobile,
    string? Nid,
    DateTime? DateOfBirth,
    string? Gender,
    string? BloodGroup,
    string? Address,
    string? EmergencyContactName,
    string? EmergencyContactPhone
);

public record PatientResponse(
    int Id,
    string PatientUid,
    string Name,
    string? Mobile,
    string? Gender,
    string? BloodGroup,
    DateTime CreatedAt
);

public record DuplicateCheckRequest(
    [Required] string Name,
    string? Mobile,
    DateTime? DateOfBirth
);

public record DuplicateCheckResponse(
    bool IsDuplicate,
    List<PatientResponse> Matches
);

public record PagedResponse<T>(
    List<T> Items,
    int TotalCount,
    int Page,
    int PageSize
);
