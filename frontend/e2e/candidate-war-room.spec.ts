import { expect, test, Page } from '@playwright/test';

const tenant = '1000000000';
const electionId = '7a2ec4ed-9aba-4707-aa49-a58b51e82713';
const permissions = [
  'dashboard.read',
  'elections.read',
  'elections.manage',
  'candidates.read',
  'candidates.manage',
  'polling.read',
  'polling.manage',
  'results.read',
  'results.manage',
  'finance.read',
  'finance.manage',
  'teams.read',
  'events.read'
];

function jwt() {
  const encode = (value: unknown) => Buffer.from(JSON.stringify(value)).toString('base64url');
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode({
    sub: '11111111-1111-1111-1111-111111111111',
    tenant_id: tenant,
    name: 'Candidate Agent',
    permission: permissions,
    exp: Math.floor(Date.now() / 1000) + 3600
  })}.signature`;
}

async function authenticate(page: Page) {
  await page.addInitScript((token) => {
    sessionStorage.setItem('eems.auth', JSON.stringify({
      accessToken: token,
      accessTokenExpiresAtUtc: new Date(Date.now() + 3600000).toISOString(),
      refreshToken: 'test-token',
      refreshTokenExpiresAtUtc: new Date(Date.now() + 86400000).toISOString(),
      passwordChangeRequired: false
    }));
  }, jwt());
}

test('Candidate War Room loads and renders hero profile and all 4 operational tabs', async ({ page }) => {
  await authenticate(page);

  // Mock polling centers
  await page.route(`**/api/v1/elections/${electionId}/polling-centers*`, route => route.fulfill({
    json: {
      items: [
        {
          electionCenterId: 'e1111111-1111-1111-1111-111111111111',
          centerId: 'ff36afed-ff27-43d6-88de-d6292e3098bd',
          name: 'Dhaka-1 Demo Polling Center',
          code: 'C-01',
          boothCount: 1,
          registeredVoters: 2500,
          isVerified: true
        }
      ],
      totalCount: 1,
      page: 1,
      pageSize: 50
    }
  }));

  // Mock symbols
  await page.route('**/api/v1/candidate/symbols', route => route.fulfill({
    json: [
      { id: 14, code: 'PITCHER_KOLOS', nameBn: 'কলস', nameEn: 'Pitcher (Kolos)', category: 'INDEPENDENT', iconEmoji: '🏺', isActive: true },
      { id: 3, code: 'PLOW', nameBn: 'লাঙ্গল', nameEn: 'Plow', category: 'POLITICAL_PARTY', iconEmoji: '🚜', isActive: true }
    ]
  }));

  // Mock candidates list
  await page.route(`**/api/v1/candidate/elections/${electionId}/candidates*`, route => route.fulfill({
    json: [
      {
        candidateId: 'c6522262-66f9-4e68-b76f-b8f69167f5cc',
        assignmentId: '9071691b-ded9-44b1-8d6f-ad6be641d1a8',
        name: 'Demo Candidate',
        positionName: 'সংসদ সদস্য (MP)',
        symbolId: 14,
        symbolNameBn: 'কলস',
        symbolNameEn: 'Pitcher (Kolos)',
        symbolEmoji: '🏺',
        partyName: 'স্বতন্ত্র প্রার্থী (Independent)',
        slogan: 'উন্নয়ন ও জনকল্যাণে আমরা সর্বদা প্রস্তুত',
        phone: '01700112233',
        campaignOffice: 'দোহার কেন্দ্রীয় নির্বাচনী কার্যালয়'
      }
    ]
  }));

  // Mock war-room
  await page.route(`**/api/v1/candidate/elections/${electionId}/war-room*`, route => route.fulfill({
    json: {
      electionId,
      electionName: 'Dhaka-1 Operational Demo',
      electionDate: '2026-12-15T00:00:00Z',
      areaName: 'ঢাকা-১ (দোহার-নবাবগঞ্জ)',
      candidate: {
        candidateId: 'c6522262-66f9-4e68-b76f-b8f69167f5cc',
        candidateElectionId: '9071691b-ded9-44b1-8d6f-ad6be641d1a8',
        name: 'Demo Candidate',
        positionName: 'সংসদ সদস্য (MP)',
        symbolId: 14,
        symbolNameBn: 'কলস',
        symbolNameEn: 'Pitcher (Kolos)',
        symbolEmoji: '🏺',
        partyName: 'স্বতন্ত্র প্রার্থী (Independent)',
        slogan: 'উন্নয়ন ও জনকল্যাণে আমরা সর্বদা প্রস্তুত',
        phone: '01711000000',
        campaignOffice: 'দোহার কেন্দ্রীয় নির্বাচনী ক্যাম্প'
      },
      totalCenters: 1,
      verifiedCenters: 1,
      totalBooths: 1,
      assignedBoothAgents: 2,
      boothAgentCoveragePercent: 100.0,
      totalCampaignTeams: 1,
      totalFieldMembers: 2,
      openCampaignTasks: 1,
      upcomingEventsCount: 0,
      ecCeiling: 2500000.00,
      totalCommittedExpenses: 450000.00,
      remainingEcBudget: 2050000.00,
      ecCeilingUtilizationPercent: 18.0
    }
  }));

  // Mock booth agents
  await page.route(`**/api/v1/candidate/elections/${electionId}/booth-agents*`, route => route.fulfill({
    json: [
      {
        id: 'a1111111-1111-1111-1111-111111111111',
        centerId: 'ff36afed-ff27-43d6-88de-d6292e3098bd',
        centerName: 'Dhaka-1 Demo Polling Center',
        centerCode: 'C-01',
        boothId: 'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
        boothCode: 'B-01',
        boothName: 'Main Hall Booth 1',
        candidateId: 'c6522262-66f9-4e68-b76f-b8f69167f5cc',
        candidateName: 'Demo Candidate',
        agentType: 'PRIMARY',
        fullName: 'মোহাম্মদ রফিকুল ইসলাম',
        nidNumber: '19852691234567890',
        phone: '01712345678',
        voterNumber: 'V-10293847',
        photoUrl: '',
        appointmentLetterIssued: true,
        checkedInAtBooth: null,
        status: 'PRESENT',
        notes: 'বিশ্বস্ত ও প্রশিক্ষিত',
        createdAtUtc: '2026-11-05T07:30:00Z'
      }
    ]
  }));

  // Mock voters
  await page.route(`**/api/v1/candidate/elections/${electionId}/voters*`, route => route.fulfill({
    json: [
      {
        id: 'a1111111-1111-1111-1111-111111111101',
        centerId: 'ff36afed-ff27-43d6-88de-d6292e3098bd',
        centerName: 'Dhaka-1 Demo Polling Center',
        centerCode: 'C-01',
        boothId: 'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
        boothCode: 'B-01',
        boothName: 'Main Hall Booth 1',
        voterNumber: '269123450001',
        serialNumber: 1,
        fullName: 'আব্দুল কাদের',
        fatherOrSpouseName: 'মরহুম রহমান আলী',
        gender: 'MALE',
        age: 52,
        areaName: 'দোহার বাজার পাড়া',
        category: 'SUPPORTER',
        slipIssued: true,
        hasVoted: false,
        phone: '01711223344',
        notes: 'বিশ্বস্ত ভোটার ও পরিবার প্রধান',
        createdAtUtc: '2026-11-05T07:30:00Z'
      }
    ]
  }));

  // Mock incidents
  await page.route(`**/api/v1/candidate/elections/${electionId}/incidents*`, route => route.fulfill({
    json: [
      {
        id: 'c1111111-1111-1111-1111-111111111101',
        centerId: 'ff36afed-ff27-43d6-88de-d6292e3098bd',
        centerName: 'Dhaka-1 Demo Polling Center',
        centerCode: 'C-01',
        boothId: 'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
        boothCode: 'B-01',
        boothName: 'Main Hall Booth 1',
        incidentType: 'BOOTH_AGENT_EXPELLED',
        severity: 'CRITICAL',
        title: '১ নং বুথ থেকে পোলিং এজেন্টকে জোরপূর্বক বের করে দেওয়ার চেষ্টা',
        description: 'সকাল ৮:১৫ ঘটিকায় প্রতিপক্ষ প্রার্থীর সমর্থকরা ১ নং বুথে প্রবেশ করে আমাদের নিয়োজিত পোলিং এজেন্টকে হুমকি প্রদর্শন করে।',
        reportedBy: 'মোহাম্মদ রফিকুল ইসলাম (পোলিং এজেন্ট)',
        reportedByPhone: '01712345678',
        reportedAt: '2026-11-05T08:15:00Z',
        status: 'SUBMITTED_TO_EC',
        evidenceAttachmentUrl: '/evidence/incident_c01_b01.jpg',
        magistrateName: 'মোঃ জাহিদুল ইসলাম (নির্বাহী ম্যাজিস্ট্রেট)',
        actionTaken: 'ম্যাজিস্ট্রেট ও স্ট্রাইকিং ফোর্স কেন্দ্রে উপস্থিত হয়ে নিরাপত্তা জোরদার করেছেন।',
        officialComplaintGenerated: true,
        createdAtUtc: '2026-11-05T08:15:00Z'
      }
    ]
  }));

  // Mock results summary
  await page.route(`**/api/v1/candidate/elections/${electionId}/results-summary*`, route => route.fulfill({
    json: {
      candidateId: 'c6522262-66f9-4e68-b76f-b8f69167f5cc',
      candidateName: 'Demo Candidate',
      candidateSymbolBn: 'কলস',
      candidateSymbolEmoji: '🏺',
      runnerUpCandidateName: 'তারেক হাসান',
      runnerUpSymbolBn: 'লাঙ্গল',
      runnerUpSymbolEmoji: '🚜',
      totalCenters: 1,
      countedCenters: 1,
      pendingCenters: 0,
      candidateTotalVotes: 1450,
      runnerUpTotalVotes: 820,
      leadMargin: 630,
      isLeading: true,
      centers: [
        {
          electionCenterId: 'e1111111-1111-1111-1111-111111111111',
          centerId: 'ff36afed-ff27-43d6-88de-d6292e3098bd',
          centerCode: 'C-01',
          centerName: 'Dhaka-1 Demo Polling Center',
          candidateVotes: 1450,
          runnerUpVotes: 820,
          margin: 630,
          isCounted: true,
          form8Verified: true,
          reportedAtUtc: '2026-11-05T08:35:00Z'
        }
      ]
    }
  }));

  // Mock EC expense schedule
  await page.route(`**/api/v1/candidate/elections/${electionId}/expenses/ec-schedule*`, route => route.fulfill({
    json: {
      ecCeiling: 2500000.00,
      totalCommitted: 450000.00,
      remainingBudget: 2050000.00,
      isWithinCeiling: true,
      utilizationPercentage: 18.0,
      categories: [
        {
          nameBn: 'প্রচারপত্র, পোস্টার, ব্যানার ও লিফলেট',
          nameEn: 'Posters, Banners & Leaflets',
          allocatedAmount: 600000.00,
          spentAmount: 120000.00,
          remainingAmount: 480000.00,
          voucherCount: 4
        }
      ]
    }
  }));

  // Navigate to war room
  await page.goto(`/elections/${electionId}/candidate-war-room`);

  // Verify Hero Banner
  await expect(page.locator('.candidate-name')).toContainText('Demo Candidate');
  await expect(page.locator('.hero-symbol-avatar')).toContainText('🏺');
  await expect(page.locator('.hero-slogan')).toContainText('উন্নয়ন ও জনকল্যাণে আমরা সর্বদা প্রস্তুত');

  // Verify Tab 1 (Overview)
  await expect(page.getByText('কমান্ড সেন্টার সংক্ষেপ')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'ভোটকেন্দ্র ও পোলিং এজেন্ট' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'নির্বাচনী ব্যয় ও ইসি সিলিং' })).toBeVisible();

  // Switch to Tab 2: Booth Agents & Form-9
  await page.getByText(/পোলিং এজেন্ট ও ফরম-৯/).click();
  await expect(page.getByText('মোহাম্মদ রফিকুল ইসলাম')).toBeVisible();
  await expect(page.getByText('Main Hall Booth 1')).toBeVisible();

  // Test opening Form-9 print preview
  await page.getByRole('button', { name: '📄 ফরম-৯' }).click();
  await expect(page.getByText('ফরম - ৯')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'পোলিং এজেন্ট নিয়োগপত্র', exact: true })).toBeVisible();
  await page.locator('.print-preview-card .close-btn').click();

  // Switch to Tab 3: Voter Roll & Voter Slips
  await page.getByText(/ভোটার ও স্লিপ/).click();
  await expect(page.getByText('আব্দুল কাদের')).toBeVisible();
  await expect(page.getByText('269123450001')).toBeVisible();

  // Test opening Voter Slips batch print modal
  await page.getByRole('button', { name: '🖨️ ব্যাচ ভোটার স্লিপ প্রিন্ট' }).click();
  await expect(page.getByText('ভোটার স্লিপ প্রিন্ট প্রিভিউ')).toBeVisible();
  await expect(page.locator('.voter-slips-grid')).toContainText('আব্দুল কাদের');
  await page.locator('.wide-slip-modal .close-btn').click();

  // Switch to Tab 4: Incidents & Magistrate Complaint
  await page.getByText(/সংকট ও অভিযোগ/).click();
  await expect(page.getByText('১ নং বুথ থেকে পোলিং এজেন্টকে জোরপূর্বক বের করে দেওয়ার চেষ্টা')).toBeVisible();

  // Test opening Magistrate Complaint Letter modal
  await page.getByRole('button', { name: '📜 ম্যাজিস্ট্রেট অভিযোগপত্র প্রিন্ট' }).click();
  await expect(page.getByText('নির্বাচনী আচরণবিধি লঙ্ঘন ও অনিয়ম প্রতিকারের আবেদন')).toBeVisible();
  await expect(page.getByText('সহকারী রিটার্নিং অফিসার / বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট')).toBeVisible();
  await page.locator('.print-preview-card .close-btn').click();

  // Switch to Tab 5: Live Results
  await page.getByRole('button', { name: '🗳️ লাইভ ফলাফল ও লিড ট্র্যাকার' }).click();
  await expect(page.getByText('LIVE LEAD MARGIN')).toBeVisible();
  await expect(page.getByText('1,450 ভোট')).toBeVisible();
  await expect(page.getByText('820 ভোট')).toBeVisible();

  // Switch to Tab 6: EC Expense Compliance Schedule
  await page.getByRole('button', { name: '💰 ইসি ব্যয় রিটার্ন বিবরণী' }).click();
  await expect(page.getByText('EC Expense Schedule')).toBeVisible();
  await expect(page.getByText('Posters, Banners & Leaflets')).toBeVisible();
});
