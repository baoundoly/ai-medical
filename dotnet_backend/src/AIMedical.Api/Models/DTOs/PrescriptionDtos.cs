using System.ComponentModel.DataAnnotations;

namespace AIMedical.Api.Models.DTOs;

public record PrescriptionItemRequest(
    [Required] string MedicineName,
    [Required] string Dosage,
    [Required] string Frequency,
    [Required] string Duration,
    string? MealInstruction
);

public record PrescriptionCreateRequest(
    [Required] int VisitId,
    [Required] int PatientId,
    [Required] List<PrescriptionItemRequest> Items
);

public record PrescriptionSignRequest(
    [Required] string SignatureMethod,
    string? DigitalSignatureHash
);

public record VoicePrescriptionRequest([Required] string AudioBase64);

public record PrescriptionItemResponse(
    int Id,
    string MedicineName,
    string Dosage,
    string Frequency,
    string Duration,
    string? MealInstruction
);

public record PrescriptionResponse(
    int Id,
    int VisitId,
    int PatientId,
    string PatientName,
    int DoctorId,
    string DoctorName,
    string Status,
    DateTime? SignedAt,
    DateTime CreatedAt,
    List<PrescriptionItemResponse> Items
);
