SET app.tenant_id = '704c25fe-4422-4960-8907-49ccaedd309b';

UPDATE election.candidates
SET name = 'তারেক হাসান',
    party_name_bn = 'জাতীয় পার্টি',
    party_name_en = 'Jatiya Party',
    slogan = 'শান্তি, উন্নয়ন ও প্রগতির অঙ্গীকার'
WHERE candidate_id = 'c8888888-8888-8888-8888-888888888888';

UPDATE election.candidate_elections
SET party_name = 'জাতীয় পার্টি',
    slogan = 'শান্তি, উন্নয়ন ও প্রগতির অঙ্গীকার'
WHERE candidate_id = 'c8888888-8888-8888-8888-888888888888';

