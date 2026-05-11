using System.ComponentModel.DataAnnotations;

namespace AIMedical.Api.Models.DTOs;

public record VisitCreateRequest(
    [Required] int PatientId,
    [Required] int DoctorId,
    int? AssistantId,
    string? ChiefComplaint,
    string? Hpi,
    string? Ros,
    string? PastHistory,
    string? FamilyHistory,
    string? SocialHistory
);

public record VisitUpdateRequest(
    string? ChiefComplaint,
    string? Hpi,
    string? Ros,
    string? PastHistory,
    string? FamilyHistory,
    string? SocialHistory,
    string? AiSummary,
    string? Status
);

public record VisitResponse(
    int Id,
    int PatientId,
    string PatientName,
    int DoctorId,
    string DoctorName,
    DateTime VisitDate,
    string Status,
    string? ChiefComplaint,
    string? AiSummary,
    DateTime? DoctorApprovedAt
);

public record VisitApproveRequest(string? Notes);
