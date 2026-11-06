import { expect, test, Page } from '@playwright/test';

const tenant = '1000000000';
const electionId = '7a2ec4ed-9aba-4707-aa49-a58b51e82713';
const permissions = [
  'dashboard.read',
  'elections.read',
  'elections.manage',
  'candidates.read',
  'candidates.manage',
  'iam.users.manage',
  'iam.roles.manage',
  'polling.read',
  'polling.manage',
  'results.read',
  'results.manage'
];

function jwt() {
  const encode = (value: unknown) => Buffer.from(JSON.stringify(value)).toString('base64url');
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode({
    sub: '11111111-1111-1111-1111-111111111111',
    tenant_id: tenant,
    name: 'Super Admin',
    permission: permissions,
    is_super_admin: 'true',
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
      passwordChangeRequired: false,
      isSuperAdmin: true
    }));
  }, jwt());
}

test('Candidate Information Entry Page loads and interacts with live preview', async ({ page }) => {
  await authenticate(page);

  // Mock candidates
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

  // Mock symbols
  await page.route('**/api/v1/candidate/symbols*', route => route.fulfill({
    json: [
      { id: 14, code: 'PITCHER_KOLOS', nameBn: 'কলস', nameEn: 'Pitcher (Kolos)', category: 'INDEPENDENT', iconEmoji: '🏺' },
      { id: 3, code: 'PLOW', nameBn: 'লাঙ্গল', nameEn: 'Plow', category: 'POLITICAL_PARTY', iconEmoji: '🚜' }
    ]
  }));

  // Mock elections
  await page.route('**/api/v1/elections', route => route.fulfill({
    json: [
      {
        electionId,
        name: 'Dhaka-1 Operational Demo',
        electionTypeId: 1,
        areaId: 1,
        lifecycleStateId: 2,
        electionDate: '2026-12-15T00:00:00Z',
        version: 1
      }
    ]
  }));

  // Mock lookups
  await page.route('**/api/v1/elections/lookups*', route => route.fulfill({
    json: {
      electionTypes: [{ id: 1, code: 'PARLIAMENTARY', name: 'জাতীয় সংসদ নির্বাচন' }],
      lifecycleStates: [{ id: 2, code: 'ACTIVE', name: 'সক্রিয়', isTerminal: false }],
      positions: [{ id: 1, code: 'MP', name: 'সংসদ সদস্য (MP)', electionTypeId: 1 }],
      areas: [{ id: 1, parentAreaId: null, areaTypeId: 1, code: 'DHK-01', nameBn: 'ঢাকা-১ (দোহার-নবাবগঞ্জ)', nameEn: 'Dhaka-1' }]
    }
  }));

  await page.goto('/candidates/entry');

  // Verify Header
  await expect(page.locator('.page-title')).toContainText('প্রার্থী তথ্য ও নির্বাচনী মার্কা এন্ট্রি');

  // Verify Form Fields
  await expect(page.locator('#candidateName')).toBeVisible();
  await expect(page.locator('#symbolSelect')).toBeVisible();
  await expect(page.locator('#partyName')).toBeVisible();
  await expect(page.locator('#candidateSlogan')).toBeVisible();

  // Verify Live Preview Card
  await expect(page.locator('.preview-card')).toBeVisible();
  await expect(page.locator('.preview-symbol-box')).toBeVisible();

  // Type a candidate name and check live preview reactivity
  await page.locator('#candidateName').fill('অধ্যাপক মোহাম্মদ ইউনুস আলী');
  await expect(page.locator('.preview-candidate-name')).toContainText('অধ্যাপক মোহাম্মদ ইউনুস আলী');

  // Type a slogan and check live preview
  await page.locator('#candidateSlogan').fill('জনকল্যাণে আমরা অঙ্গীকারবদ্ধ');
  await expect(page.locator('.preview-slogan')).toContainText('জনকল্যাণে আমরা অঙ্গীকারবদ্ধ');
});

test('User Creation Page loads, provides username suggestions, and lists users', async ({ page }) => {
  await authenticate(page);

  // Mock users
  await page.route('**/api/v1/admin/users*', route => route.fulfill({
    json: [
      {
        userId: 'u1111111-1111-1111-1111-111111111111',
        displayName: 'সুপার অ্যাডমিন',
        username: 'admin',
        email: 'admin@eems.local',
        isActive: true,
        roleCodes: ['TENANT_ADMIN'],
        candidateId: null,
        candidateName: null
      },
      {
        userId: 'u2222222-2222-2222-2222-222222222222',
        displayName: 'তৌসিফ আহমেদ',
        username: 'tousif',
        email: 'tousif@kolos.campaign',
        isActive: true,
        roleCodes: ['CAMPAIGN_MANAGER'],
        candidateId: 'c6522262-66f9-4e68-b76f-b8f69167f5cc',
        candidateName: 'Demo Candidate'
      }
    ]
  }));

  // Mock roles
  await page.route('**/api/v1/admin/roles*', route => route.fulfill({
    json: [
      { roleId: 'r1111111-1111-1111-1111-111111111111', code: 'TENANT_ADMIN', name: 'সিস্টেম অ্যাডমিন', permissions: [] },
      { roleId: 'r2222222-2222-2222-2222-222222222222', code: 'CAMPAIGN_MANAGER', name: 'নির্বাচনী সমন্বয়কারী', permissions: [] }
    ]
  }));

  // Mock candidates
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

  await page.goto('/administration/users');

  // Verify Header
  await expect(page.locator('.page-title')).toContainText('ব্যবহারকারী তৈরি ও প্রার্থী স্কোপ নির্ধারণ');

  // Verify Form inputs
  await expect(page.locator('#fullName')).toBeVisible();
  await expect(page.locator('#usernameInput')).toBeVisible();
  await expect(page.locator('#candidateSelect')).toBeVisible();
  await expect(page.locator('#roleSelect')).toBeVisible();
  await expect(page.locator('#passwordInput')).toBeVisible();

  // Type a full name and verify Suggest Username functionality
  await page.locator('#fullName').fill('Mohammad Mostafa');
  await page.locator('.btn-suggest').click();
  const usernameVal = await page.locator('#usernameInput').inputValue();
  expect(usernameVal).toContain('mohammad.mostafa');

  // Verify table is visible
  await expect(page.locator('.users-table')).toBeVisible();
  await expect(page.locator('.users-table')).toContainText('তৌসিফ আহমেদ');
  await expect(page.locator('.users-table')).toContainText('Demo Candidate');
});
