using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class EventDocument : Entity<Guid>
{
    private EventDocument() { }
    private EventDocument(Guid id, Guid tenantId, Guid eventId, Guid uploadedByUserId, string fileName,
        string storageKey, string contentType, string checksum)
    {
        if (tenantId == Guid.Empty || eventId == Guid.Empty || uploadedByUserId == Guid.Empty)
            throw new ArgumentException("Tenant, event and uploader are required.");
        Id = id;
        TenantId = tenantId;
        EventId = eventId;
        UploadedByUserId = uploadedByUserId;
        FileName = TextRules.Required(fileName, 255);
        StorageKey = TextRules.Required(storageKey, 500);
        ContentType = TextRules.Required(contentType, 120);
        Checksum = TextRules.Required(checksum, 128);
        UploadedAtUtc = DateTimeOffset.UtcNow;
    }

    public Guid TenantId { get; private set; }
    public Guid EventId { get; private set; }
    public Guid UploadedByUserId { get; private set; }
    public string FileName { get; private set; } = string.Empty;
    public string StorageKey { get; private set; } = string.Empty;
    public string ContentType { get; private set; } = string.Empty;
    public string Checksum { get; private set; } = string.Empty;
    public DateTimeOffset UploadedAtUtc { get; private set; }

    public static EventDocument Create(Guid tenantId, Guid eventId, Guid uploadedByUserId, string fileName,
        string storageKey, string contentType, string checksum) =>
        new(Guid.NewGuid(), tenantId, eventId, uploadedByUserId, fileName, storageKey, contentType, checksum);
}
