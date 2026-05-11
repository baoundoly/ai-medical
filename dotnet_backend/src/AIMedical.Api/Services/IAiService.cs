namespace AIMedical.Api.Services;

public interface IAiService
{
    Task<string?> TranscribeAudioAsync(string audioBase64);
    Task<string?> GetAiSummaryAsync(string visitText);
    Task<string?> SuggestDiagnosisAsync(string symptoms);
    Task<string?> ParseVoicePrescriptionAsync(string audioBase64);
    Task<string?> CheckDrugInteractionsAsync(IEnumerable<string> medicines);
}
