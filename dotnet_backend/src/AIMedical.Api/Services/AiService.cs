using System.Net.Http.Json;
using System.Text.Json;

namespace AIMedical.Api.Services;

public class AiService : IAiService
{
    private readonly HttpClient _http;
    private readonly ILogger<AiService> _logger;

    public AiService(HttpClient http, ILogger<AiService> logger)
    {
        _http = http;
        _logger = logger;
    }

    public async Task<string?> TranscribeAudioAsync(string audioBase64)
        => await PostAndGetStringAsync("/api/ai/transcribe", new { audio_base64 = audioBase64 }, "transcription");

    public async Task<string?> GetAiSummaryAsync(string visitText)
        => await PostAndGetStringAsync("/api/ai/summarize", new { text = visitText }, "summary");

    public async Task<string?> SuggestDiagnosisAsync(string symptoms)
        => await PostAndGetStringAsync("/api/ai/diagnose", new { symptoms }, "suggestions");

    public async Task<string?> ParseVoicePrescriptionAsync(string audioBase64)
        => await PostAndGetStringAsync("/api/ai/voice-prescription", new { audio_base64 = audioBase64 }, "prescription");

    public async Task<string?> CheckDrugInteractionsAsync(IEnumerable<string> medicines)
        => await PostAndGetStringAsync("/api/ai/drug-interactions", new { medicines }, "interactions");

    private async Task<string?> PostAndGetStringAsync(string path, object payload, string resultKey)
    {
        try
        {
            var response = await _http.PostAsJsonAsync(path, payload);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(json);

            if (doc.RootElement.TryGetProperty(resultKey, out var el))
                return el.GetString();

            return json;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "AI layer call to {Path} failed", path);
            return null;
        }
    }
}
