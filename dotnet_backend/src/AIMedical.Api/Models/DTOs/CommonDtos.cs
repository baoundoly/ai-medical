namespace AIMedical.Api.Models.DTOs;

public record ApiResponse<T>(bool Success, string? Message, T? Data);

public record ApiError(string Message, string? Details = null);

public record PaginationParams(int Page = 1, int PageSize = 20);

public record NotificationResponse(
    int Id,
    string Title,
    string Body,
    string Type,
    bool IsRead,
    DateTime CreatedAt
);

public record AnalyticsTrendResponse(
    string Label,
    int Count,
    DateTime Period
);
