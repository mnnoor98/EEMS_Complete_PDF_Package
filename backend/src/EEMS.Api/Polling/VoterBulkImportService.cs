using System.Text;
using System.Text.RegularExpressions;
using EEMS.Api.Controllers;
using EEMS.Modules.Polling.Domain;
using EEMS.Modules.Polling.Infrastructure;
using ExcelDataReader;
using Microsoft.EntityFrameworkCore;
using UglyToad.PdfPig;

namespace EEMS.Api.Polling;

public sealed record VoterBulkRowDto(
    int SerialNumber,
    string VoterNumber,
    string FullName,
    string? FatherOrSpouseName,
    string Gender,
    int? Age,
    string? AreaName,
    string Category,
    string? Phone,
    string? Notes,
    string? CenterCode = null,
    string? BoothCode = null,
    bool IsValid = true,
    string? ValidationMessage = null);

public sealed record VoterBulkPreviewResult(
    int TotalFound,
    int ValidCount,
    int InvalidCount,
    string FileName,
    string DetectedFormat,
    IReadOnlyList<VoterBulkRowDto> Rows,
    IReadOnlyList<string> Warnings);

public sealed record VoterBulkImportResult(
    bool Success,
    int InsertedCount,
    int SkippedCount,
    string Message,
    IReadOnlyList<CandidateVoterSummary> ImportedVoters);

public sealed partial class VoterBulkImportService(
    PollingDbContext pollingDb)
{
    static VoterBulkImportService()
    {
        // Register code pages provider for ExcelDataReader support on older .xls
        Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
    }

    public async Task<VoterBulkPreviewResult> PreviewFileAsync(
        Guid tenantId,
        Guid electionId,
        Guid centerId,
        Guid? boothId,
        IFormFile file,
        CancellationToken cancellationToken)
    {
        if (file == null || file.Length == 0)
        {
            throw new ArgumentException("কোনো ফাইল প্রদান করা হয়নি বা ফাইলটি ফাঁকা।");
        }

        var baseCenter = await pollingDb.Centers.FirstOrDefaultAsync(c => c.Id == centerId, cancellationToken);
        if (baseCenter == null)
        {
            var ec = await pollingDb.ElectionCenters.FirstOrDefaultAsync(x => x.Id == centerId, cancellationToken);
            if (ec != null)
            {
                centerId = ec.CenterId;
            }
        }

        var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
        var rows = new List<VoterBulkRowDto>();
        var warnings = new List<string>();
        string detectedFormat;

        await using var stream = file.OpenReadStream();

        if (ext is ".csv" or ".txt" or ".tsv")
        {
            detectedFormat = "CSV / Plain Text";
            rows = await ParseCsvAsync(stream, cancellationToken);
        }
        else if (ext is ".xlsx" or ".xls")
        {
            detectedFormat = ext == ".xlsx" ? "Microsoft Excel (.xlsx)" : "Microsoft Excel 97-2003 (.xls)";
            rows = ParseExcel(stream);
        }
        else if (ext is ".pdf")
        {
            detectedFormat = "Adobe PDF (.pdf)";
            rows = ParsePdf(stream);
        }
        else
        {
            throw new NotSupportedException($"অসমর্থিত ফাইল ফরম্যাট ({ext})। শুধুমাত্র CSV, Excel (.xlsx, .xls) ও PDF (.pdf) ফাইল সমর্থনযোগ্য।");
        }

        if (rows.Count == 0)
        {
            warnings.Add("ফাইলটি থেকে কোনো বৈধ ভোটার রেকর্ড শনাক্ত করা যায়নি। অনুগ্রহ করে ফাইল ফরম্যাট ও কলাম যাচাই করুন।");
        }

        // Validate each row
        var existingVotersList = await pollingDb.Voters
            .Where(v => v.TenantId == tenantId && v.ElectionId == electionId)
            .Select(v => v.VoterNumber)
            .ToListAsync(cancellationToken);
        var existingVoters = existingVotersList.ToHashSet(StringComparer.OrdinalIgnoreCase);

        var validatedRows = new List<VoterBulkRowDto>(rows.Count);
        int validCount = 0;
        int invalidCount = 0;

        foreach (var r in rows)
        {
            var msgList = new List<string>();
            bool isValid = true;

            if (string.IsNullOrWhiteSpace(r.VoterNumber))
            {
                isValid = false;
                msgList.Add("ভোটার নম্বর অনুপস্থিত");
            }
            else if (existingVoters.Contains(r.VoterNumber.Trim()))
            {
                msgList.Add("এই ভোটার নম্বরটি সিস্টেমে ইতিমধ্যেই নিবন্ধিত (ডুপ্লিকেট)");
            }

            if (string.IsNullOrWhiteSpace(r.FullName))
            {
                isValid = false;
                msgList.Add("ভোটারের নাম অনুপস্থিত");
            }

            if (isValid) validCount++; else invalidCount++;

            validatedRows.Add(r with
            {
                IsValid = isValid,
                ValidationMessage = msgList.Count > 0 ? string.Join("; ", msgList) : null
            });
        }

        return new VoterBulkPreviewResult(
            validatedRows.Count,
            validCount,
            invalidCount,
            file.FileName,
            detectedFormat,
            validatedRows,
            warnings);
    }

    public async Task<VoterBulkImportResult> ImportRowsAsync(
        Guid tenantId,
        Guid electionId,
        Guid defaultCenterId,
        Guid? defaultBoothId,
        Guid? candidateId,
        IReadOnlyList<VoterBulkRowDto> rows,
        CancellationToken cancellationToken)
    {
        if (rows == null || rows.Count == 0)
        {
            return new VoterBulkImportResult(false, 0, 0, "আমদানি করার জন্য কোনো ভোটার তথ্য পাওয়া যায়নি।", Array.Empty<CandidateVoterSummary>());
        }

        var electionCenters = await pollingDb.Centers
            .ToListAsync(cancellationToken);

        var baseCenter = electionCenters.FirstOrDefault(c => c.Id == defaultCenterId);
        if (baseCenter == null)
        {
            var ec = await pollingDb.ElectionCenters.FirstOrDefaultAsync(x => x.Id == defaultCenterId, cancellationToken);
            if (ec != null)
            {
                defaultCenterId = ec.CenterId;
            }
        }
        var centersByCode = electionCenters
            .Where(c => !string.IsNullOrEmpty(c.Code))
            .GroupBy(c => c.Code.Trim().ToUpperInvariant())
            .ToDictionary(g => g.Key, g => g.First().Id);

        var allBooths = await pollingDb.Booths
            .ToListAsync(cancellationToken);
        var boothsByCenterAndCode = allBooths
            .Where(b => !string.IsNullOrEmpty(b.Code))
            .GroupBy(b => $"{b.CenterId}_{b.Code.Trim().ToUpperInvariant()}")
            .ToDictionary(g => g.Key, g => g.First().Id);
        var boothsByCodeOnly = allBooths
            .Where(b => !string.IsNullOrEmpty(b.Code))
            .GroupBy(b => b.Code.Trim().ToUpperInvariant())
            .ToDictionary(g => g.Key, g => g.First().Id);

        var existingVoterList = await pollingDb.Voters
            .Where(v => v.TenantId == tenantId && v.ElectionId == electionId)
            .Select(v => v.VoterNumber)
            .ToListAsync(cancellationToken);
        var existingVoterNumbers = existingVoterList.ToHashSet(StringComparer.OrdinalIgnoreCase);

        var votersToAdd = new List<Voter>();
        var importedSummaries = new List<CandidateVoterSummary>();
        int skippedCount = 0;

        foreach (var r in rows)
        {
            if (!r.IsValid || string.IsNullOrWhiteSpace(r.VoterNumber) || string.IsNullOrWhiteSpace(r.FullName))
            {
                skippedCount++;
                continue;
            }

            var cleanVoterNumber = r.VoterNumber.Trim();
            if (existingVoterNumbers.Contains(cleanVoterNumber))
            {
                skippedCount++;
                continue; // Skip duplicate voter
            }

            // Resolve center
            Guid targetCenterId = defaultCenterId;
            if (!string.IsNullOrWhiteSpace(r.CenterCode) && centersByCode.TryGetValue(r.CenterCode.Trim().ToUpperInvariant(), out var matchedCenterId))
            {
                targetCenterId = matchedCenterId;
            }

            // Resolve booth
            Guid? targetBoothId = defaultBoothId;
            if (!string.IsNullOrWhiteSpace(r.BoothCode))
            {
                var cleanBoothCode = r.BoothCode.Trim().ToUpperInvariant();
                if (boothsByCenterAndCode.TryGetValue($"{targetCenterId}_{cleanBoothCode}", out var matchedBoothId) ||
                    boothsByCodeOnly.TryGetValue(cleanBoothCode, out matchedBoothId))
                {
                    targetBoothId = matchedBoothId;
                }
            }

            var voter = Voter.Create(
                tenantId,
                electionId,
                targetCenterId,
                targetBoothId,
                cleanVoterNumber,
                r.SerialNumber > 0 ? r.SerialNumber : (votersToAdd.Count + 1),
                r.FullName.Trim(),
                r.FatherOrSpouseName?.Trim(),
                NormalizeGender(r.Gender),
                r.Age,
                r.AreaName?.Trim(),
                NormalizeCategory(r.Category),
                r.Phone?.Trim(),
                r.Notes?.Trim(),
                candidateId);

            votersToAdd.Add(voter);
            existingVoterNumbers.Add(cleanVoterNumber);
        }

        if (votersToAdd.Count > 0)
        {
            pollingDb.Voters.AddRange(votersToAdd);
            await pollingDb.SaveChangesAsync(cancellationToken);

            var centerDict = electionCenters.ToDictionary(c => c.Id, c => c);
            var boothDict = allBooths.ToDictionary(b => b.Id, b => b);

            foreach (var v in votersToAdd.Take(50)) // Return first 50 created
            {
                centerDict.TryGetValue(v.CenterId, out var c);
                Booth? b = null;
                if (v.BoothId.HasValue) boothDict.TryGetValue(v.BoothId.Value, out b);

                importedSummaries.Add(new CandidateVoterSummary(
                    v.Id,
                    v.CenterId,
                    c?.Name ?? "ভোটকেন্দ্র",
                    c?.Code ?? string.Empty,
                    v.BoothId,
                    b?.Code,
                    b?.Name,
                    v.VoterNumber,
                    v.SerialNumber,
                    v.FullName,
                    v.FatherOrSpouseName,
                    v.Gender,
                    v.Age,
                    v.AreaName,
                    v.Category,
                    v.SlipIssued,
                    v.HasVoted,
                    v.Phone,
                    v.Notes,
                    v.CreatedAtUtc,
                    v.CandidateId));
            }
        }

        return new VoterBulkImportResult(
            true,
            votersToAdd.Count,
            skippedCount,
            $"মোট {votersToAdd.Count} জন ভোটার ডাটাবেসে সফলভাবে যুক্ত করা হয়েছে। (বাদ/ডুপ্লিকেট: {skippedCount} জন)",
            importedSummaries);
    }

    public static byte[] GenerateSampleCsvTemplate()
    {
        var sb = new StringBuilder();
        // UTF-8 BOM
        sb.Append('\uFEFF');
        // Header
        sb.AppendLine("ক্রমিক নং,ভোটার আইডি (NID),ভোটারের পূর্ণ নাম,পিতা বা স্বামীর নাম,লিঙ্গ,বয়স,গ্রাম/পাড়া/এলাকা,ক্যাটাগরি,মোবাইল নম্বর,মন্তব্য");
        // Sample rows with realistic data
        sb.AppendLine("১,1990123456789,মোহাম্মদ রফিকুল ইসলাম,মরহুম জহিরুল ইসলাম,পুরুষ,৩৫,বরইয়া,SUPPORTER,01711223344,বিশ্বস্ত কর্মী");
        sb.AppendLine("২,1992987654321,নাসরিন আক্তার,মোহাম্মদ রফিকুল ইসলাম,নারী,৩২,বরইয়া,SUPPORTER,01811223344,পোলিং কাজে সহায়তা");
        sb.AppendLine("৩,1985445566778,আব্দুল কাদের,মোঃ রহিম উল্লাহ,পুরুষ,৪০,পুর্ব রামপুর,SWING,01911223344,নিরপেক্ষ ভোটার");
        sb.AppendLine("৪,1978332211009,মোসাঃ ফাতেমা বেগম,মোঃ আব্দুল খালেক,নারী,৪৬,উত্তর করিমপুর,SUPPORTER,01611223344,স্লিপ বিতরণ সম্পন্ন");
        sb.AppendLine("৫,1998556677889,তানভীর হাসান,মোঃ কামাল উদ্দিন,পুরুষ,২৬,দক্ষিণ বাজার,ABROAD,01511223344,বর্তমানে সৌদি আরবে অবস্থানরত");
        return Encoding.UTF8.GetBytes(sb.ToString());
    }

    // -------------------------------------------------------------------------
    // PARSERS
    // -------------------------------------------------------------------------

    private static async Task<List<VoterBulkRowDto>> ParseCsvAsync(Stream stream, CancellationToken cancellationToken)
    {
        var list = new List<VoterBulkRowDto>();
        using var reader = new StreamReader(stream, Encoding.UTF8, detectEncodingFromByteOrderMarks: true, leaveOpen: true);
        
        string? headerLine = await reader.ReadLineAsync(cancellationToken);
        if (string.IsNullOrWhiteSpace(headerLine)) return list;

        char delimiter = DetectDelimiter(headerLine);
        var headers = SplitCsvLine(headerLine, delimiter);
        var colMap = MapHeaders(headers);

        int rowNum = 1;
        string? line;
        while ((line = await reader.ReadLineAsync(cancellationToken)) != null)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;

            var cols = SplitCsvLine(line, delimiter);
            if (cols.Count == 0 || cols.All(string.IsNullOrWhiteSpace)) continue;

            var row = ExtractRow(cols, colMap, rowNum++);
            if (row != null) list.Add(row);
        }

        return list;
    }

    private static List<VoterBulkRowDto> ParseExcel(Stream stream)
    {
        var list = new List<VoterBulkRowDto>();
        using var reader = ExcelReaderFactory.CreateReader(stream);

        // Read first sheet
        if (!reader.Read()) return list;

        // Header row
        var headers = new List<string>();
        for (int i = 0; i < reader.FieldCount; i++)
        {
            headers.Add(reader.GetValue(i)?.ToString()?.Trim() ?? string.Empty);
        }

        // If row was empty, advance until we find headers
        while (headers.All(string.IsNullOrWhiteSpace) && reader.Read())
        {
            headers.Clear();
            for (int i = 0; i < reader.FieldCount; i++)
            {
                headers.Add(reader.GetValue(i)?.ToString()?.Trim() ?? string.Empty);
            }
        }

        var colMap = MapHeaders(headers);
        int rowNum = 1;

        while (reader.Read())
        {
            var cols = new List<string>();
            for (int i = 0; i < reader.FieldCount; i++)
            {
                var val = reader.GetValue(i);
                cols.Add(val?.ToString()?.Trim() ?? string.Empty);
            }

            if (cols.All(string.IsNullOrWhiteSpace)) continue;

            var row = ExtractRow(cols, colMap, rowNum++);
            if (row != null) list.Add(row);
        }

        return list;
    }

    private static List<VoterBulkRowDto> ParsePdf(Stream stream)
    {
        var list = new List<VoterBulkRowDto>();
        using var pdf = PdfDocument.Open(stream);

        int rowNum = 1;
        var linesBuffer = new List<string>();

        foreach (var page in pdf.GetPages())
        {
            var text = page.Text;
            if (string.IsNullOrWhiteSpace(text)) continue;

            var rawLines = text.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var l in rawLines)
            {
                var trimmed = l.Trim();
                if (!string.IsNullOrEmpty(trimmed)) linesBuffer.Add(trimmed);
            }
        }

        if (linesBuffer.Count == 0) return list;

        // Check if there is a header line in PDF text
        int headerIndex = -1;
        Dictionary<string, int>? colMap = null;

        for (int i = 0; i < Math.Min(10, linesBuffer.Count); i++)
        {
            var line = linesBuffer[i];
            if (line.Contains("ক্রমিক") || line.Contains("ভোটার") || line.Contains("নাম") || line.Contains("Voter") || line.Contains("Name"))
            {
                char delimiter = DetectDelimiter(line);
                var tokens = SplitCsvLine(line, delimiter);
                if (tokens.Count >= 3)
                {
                    headerIndex = i;
                    colMap = MapHeaders(tokens);
                    break;
                }
            }
        }

        if (headerIndex >= 0 && colMap != null)
        {
            for (int i = headerIndex + 1; i < linesBuffer.Count; i++)
            {
                var line = linesBuffer[i];
                char delimiter = DetectDelimiter(line);
                var cols = SplitCsvLine(line, delimiter);
                if (cols.Count >= 2 && !cols.All(string.IsNullOrWhiteSpace))
                {
                    var row = ExtractRow(cols, colMap, rowNum++);
                    if (row != null) list.Add(row);
                }
            }
        }
        else
        {
            // Freeform or tabular heuristic parser for Bangladesh Voter List PDFs
            // Pattern: Serial, 10-17 digit NID / Voter Number, Bengali Name...
            foreach (var line in linesBuffer)
            {
                // Try splitting by whitespace, tabs, or pipes
                var parts = line.Split(new[] { '|', '\t', ';' }, StringSplitOptions.RemoveEmptyEntries)
                                .Select(p => p.Trim())
                                .Where(p => !string.IsNullOrEmpty(p))
                                .ToList();

                if (parts.Count < 3)
                {
                    // Try splitting by 2 or more spaces
                    parts = Regex.Split(line, @"\s{2,}")
                                 .Select(p => p.Trim())
                                 .Where(p => !string.IsNullOrEmpty(p))
                                 .ToList();
                }

                if (parts.Count >= 2)
                {
                    // Check if one of the tokens looks like an NID / voter ID (10 to 17 digits)
                    int voterIdIdx = parts.FindIndex(p => Regex.IsMatch(ToEnglishDigits(p), @"^\d{9,17}$"));
                    if (voterIdIdx >= 0)
                    {
                        string voterNum = ToEnglishDigits(parts[voterIdIdx]);
                        int serial = rowNum;
                        string name = "";
                        string? father = null;

                        if (voterIdIdx > 0 && int.TryParse(ToEnglishDigits(parts[0]), out var s))
                        {
                            serial = s;
                        }

                        // Name is usually adjacent to voter number
                        if (voterIdIdx + 1 < parts.Count)
                        {
                            name = parts[voterIdIdx + 1];
                        }
                        else if (voterIdIdx > 1)
                        {
                            name = parts[1];
                        }

                        if (voterIdIdx + 2 < parts.Count)
                        {
                            father = parts[voterIdIdx + 2];
                        }

                        if (!string.IsNullOrWhiteSpace(name))
                        {
                            list.Add(new VoterBulkRowDto(
                                serial,
                                voterNum,
                                name,
                                father,
                                "MALE",
                                null,
                                null,
                                "SUPPORTER",
                                null,
                                null));
                            rowNum++;
                        }
                    }
                }
            }
        }

        return list;
    }

    // -------------------------------------------------------------------------
    // HELPER METHODS
    // -------------------------------------------------------------------------

    private static VoterBulkRowDto? ExtractRow(List<string> cols, Dictionary<string, int> colMap, int fallbackSerial)
    {
        string GetVal(string key) => colMap.TryGetValue(key, out int idx) && idx < cols.Count ? cols[idx].Trim() : string.Empty;

        var voterNumber = GetVal("voterNumber");
        var fullName = GetVal("fullName");

        // If header mapping couldn't find, try column index heuristics
        if (string.IsNullOrWhiteSpace(voterNumber) && cols.Count >= 2)
        {
            // Column 0 or 1 might be voter ID
            if (Regex.IsMatch(ToEnglishDigits(cols[1]), @"^\d{8,20}$"))
            {
                voterNumber = cols[1];
                fullName = cols.Count > 2 ? cols[2] : cols[0];
            }
            else if (Regex.IsMatch(ToEnglishDigits(cols[0]), @"^\d{8,20}$"))
            {
                voterNumber = cols[0];
                fullName = cols.Count > 1 ? cols[1] : string.Empty;
            }
        }

        if (string.IsNullOrWhiteSpace(voterNumber) && string.IsNullOrWhiteSpace(fullName))
        {
            return null;
        }

        voterNumber = ToEnglishDigits(voterNumber);

        // Serial
        int serial = fallbackSerial;
        var sVal = GetVal("serialNumber");
        if (!string.IsNullOrWhiteSpace(sVal) && int.TryParse(ToEnglishDigits(sVal), out var parsedS))
        {
            serial = parsedS;
        }

        // Age
        int? age = null;
        var aVal = GetVal("age");
        if (!string.IsNullOrWhiteSpace(aVal) && int.TryParse(ToEnglishDigits(aVal), out var parsedA) && parsedA is >= 18 and <= 120)
        {
            age = parsedA;
        }

        return new VoterBulkRowDto(
            serial,
            voterNumber,
            fullName,
            NullIfEmpty(GetVal("fatherOrSpouseName")),
            NormalizeGender(GetVal("gender")),
            age,
            NullIfEmpty(GetVal("areaName")),
            NormalizeCategory(GetVal("category")),
            NullIfEmpty(ToEnglishDigits(GetVal("phone"))),
            NullIfEmpty(GetVal("notes")),
            NullIfEmpty(GetVal("centerCode")),
            NullIfEmpty(GetVal("boothCode")));
    }

    private static Dictionary<string, int> MapHeaders(List<string> headers)
    {
        var map = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);

        for (int i = 0; i < headers.Count; i++)
        {
            var h = CleanHeader(headers[i]);
            if (string.IsNullOrEmpty(h)) continue;

            if (MatchesAny(h, "ক্রমিক", "ক্রমিকনং", "sl", "serial", "serialno", "serialnumber", "ক্রঃ"))
                map["serialNumber"] = i;
            else if (MatchesAny(h, "ভোটারনম্বর", "ভোটারআইডি", "ভোটারনং", "জাতীয়পরিচয়পত্র", "nid", "voterid", "voterno", "voternumber", "voter_number", "voter_id"))
                map["voterNumber"] = i;
            else if (MatchesAny(h, "পিতা", "পিতারনাম", "স্বামী", "স্বামীরনাম", "পিতা/স্বামীরনাম", "পিতাবাস্বামীরনাম", "father", "fathername", "spouse", "fatherorspouse", "fatherorspousename"))
                map["fatherOrSpouseName"] = i;
            else if (MatchesAny(h, "ভোটারেরনাম", "ভোটারেরপূর্ণনাম", "পূর্ণনাম", "ভোটারের", "name", "fullname", "votername", "voter_name") || h == "নাম")
                map["fullName"] = i;
            else if (MatchesAny(h, "লিঙ্গ", "sex", "gender"))
                map["gender"] = i;
            else if (MatchesAny(h, "বয়স", "age"))
                map["age"] = i;
            else if (MatchesAny(h, "গ্রাম", "পাড়া", "মহল্লা", "এলাকা", "গ্রাম/পাড়া", "ঠিকানা", "area", "areaname", "village", "address", "ward"))
                map["areaName"] = i;
            else if (MatchesAny(h, "ক্যাটাগরি", "শ্রেণী", "ধরণ", "category", "votercategory", "type"))
                map["category"] = i;
            else if (MatchesAny(h, "মোবাইল", "মোবাইলনম্বর", "ফোন", "ফোননম্বর", "phone", "mobile", "contact"))
                map["phone"] = i;
            else if (MatchesAny(h, "মন্তব্য", "নোট", "notes", "note", "remarks", "comment"))
                map["notes"] = i;
            else if (MatchesAny(h, "কেন্দ্রকোড", "কেন্দ্র", "centercode", "center", "center_code"))
                map["centerCode"] = i;
            else if (MatchesAny(h, "বুথকোড", "বুথ", "boothcode", "booth", "booth_code"))
                map["boothCode"] = i;
        }

        return map;
    }

    private static string CleanHeader(string h) =>
        Regex.Replace(h.ToLowerInvariant(), @"[\s_\-\.\(\)\[\]\/]", "");

    private static bool MatchesAny(string text, params string[] candidates) =>
        candidates.Any(c => text.Equals(c, StringComparison.OrdinalIgnoreCase) || text.Contains(c, StringComparison.OrdinalIgnoreCase));

    private static char DetectDelimiter(string line)
    {
        int commas = line.Count(c => c == ',');
        int tabs = line.Count(c => c == '\t');
        int semis = line.Count(c => c == ';');
        int pipes = line.Count(c => c == '|');

        if (tabs > commas && tabs > semis && tabs > pipes) return '\t';
        if (semis > commas && semis > tabs && semis > pipes) return ';';
        if (pipes > commas && pipes > tabs && pipes > semis) return '|';
        return ',';
    }

    private static List<string> SplitCsvLine(string line, char delimiter)
    {
        var result = new List<string>();
        var current = new StringBuilder();
        bool inQuotes = false;

        for (int i = 0; i < line.Length; i++)
        {
            char c = line[i];
            if (c == '"')
            {
                if (inQuotes && i + 1 < line.Length && line[i + 1] == '"')
                {
                    current.Append('"');
                    i++;
                }
                else
                {
                    inQuotes = !inQuotes;
                }
            }
            else if (c == delimiter && !inQuotes)
            {
                result.Add(current.ToString().Trim());
                current.Clear();
            }
            else
            {
                current.Append(c);
            }
        }

        result.Add(current.ToString().Trim());
        return result;
    }

    public static string ToEnglishDigits(string? input)
    {
        if (string.IsNullOrWhiteSpace(input)) return string.Empty;
        var sb = new StringBuilder(input.Length);
        foreach (char c in input)
        {
            sb.Append(c switch
            {
                '০' => '0',
                '১' => '1',
                '২' => '2',
                '৩' => '3',
                '৪' => '4',
                '৫' => '5',
                '৬' => '6',
                '৭' => '7',
                '৮' => '8',
                '৯' => '9',
                _ => c
            });
        }
        return sb.ToString().Trim();
    }

    public static string NormalizeGender(string? gender)
    {
        if (string.IsNullOrWhiteSpace(gender)) return "MALE";
        var g = gender.Trim().ToLowerInvariant();
        if (g.Contains("মহিলা") || g.Contains("নারী") || g.Contains("female") || g == "f")
            return "FEMALE";
        return "MALE";
    }

    public static string NormalizeCategory(string? cat)
    {
        if (string.IsNullOrWhiteSpace(cat)) return "SUPPORTER";
        var c = cat.Trim().ToLowerInvariant();
        if (c.Contains("নিরপেক্ষ") || c.Contains("দোদুল্যমান") || c.Contains("swing")) return "SWING";
        if (c.Contains("প্রতিপক্ষ") || c.Contains("বিরোধী") || c.Contains("opponent")) return "OPPONENT";
        if (c.Contains("প্রবাসী") || c.Contains("অনুপস্থিত") || c.Contains("abroad")) return "ABROAD";
        return "SUPPORTER";
    }

    private static string? NullIfEmpty(string? s) => string.IsNullOrWhiteSpace(s) ? null : s.Trim();
}
