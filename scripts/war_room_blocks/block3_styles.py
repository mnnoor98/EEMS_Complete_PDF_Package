# -*- coding: utf-8 -*-

def get_styles():
    return '''
    :host { display: block; padding-bottom: 40px; }
    .back { display: inline-block; margin-bottom: 14px; color: var(--navy); text-decoration: none; font-weight: 600; font-size: 0.9rem; }
    .back:hover { text-decoration: underline; }

    /* Hero Banner */
    .hero-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 22px 28px;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
      border-left: 6px solid var(--teal);
      flex-wrap: wrap;
      gap: 18px;
    }
    .hero-left { display: flex; align-items: center; gap: 20px; }
    .hero-symbol-avatar {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 82px;
      height: 82px;
      background: #f1f5f9;
      border: 2px solid #cbd5e1;
      border-radius: 14px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }
    .symbol-emoji { font-size: 2.8rem; line-height: 1; }
    .symbol-caption { font-size: 0.72rem; font-weight: 700; color: var(--teal); margin-top: 2px; }
    .hero-title-row { display: flex; align-items: center; gap: 12px; }
    .hero-title-row h2 { margin: 0; font-size: 1.6rem; color: var(--navy); }
    .hero-meta { margin: 6px 0 0; color: #475569; font-size: 0.92rem; }
    .hero-slogan { margin: 4px 0 0; font-style: italic; color: #0284c7; font-size: 0.9rem; font-weight: 500; }
    .hero-right { display: flex; gap: 12px; }
    .stat-pill {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 10px 18px;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 12px;
      min-width: 80px;
    }
    .stat-pill.highlight { background: #ecfdf5; border-color: #a7f3d0; }
    .stat-val { font-size: 1.45rem; font-weight: 800; color: var(--navy); line-height: 1.1; }
    .stat-pill.highlight .stat-val { color: #047857; }
    .stat-lbl { font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 600; margin-top: 3px; }

    /* Tab Navigation */
    .tab-nav {
      display: flex;
      gap: 6px;
      margin-bottom: 20px;
      border-bottom: 2px solid var(--line);
      padding-bottom: 6px;
      flex-wrap: wrap;
    }
    .tab-btn {
      padding: 10px 18px;
      border: none;
      background: transparent;
      font-size: 0.92rem;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      border-radius: 8px 8px 0 0;
      transition: all 0.15s ease-in-out;
      white-space: nowrap;
    }
    .tab-btn:hover { color: var(--navy); background: #f1f5f9; }
    .tab-btn.active {
      color: var(--teal);
      background: #ecfdf5;
      font-weight: 700;
      border-bottom: 3px solid var(--teal);
    }

    /* Operations Grid */
    .operations-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
      margin-bottom: 24px;
    }
    .op-card {
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border-radius: 12px;
      transition: transform 0.15s;
    }
    .op-head { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
    .op-icon { font-size: 1.9rem; }
    .op-eyebrow { margin: 0; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; }
    .op-head h3 { margin: 2px 0 0; font-size: 1.15rem; color: var(--navy); }
    .metrics-row { display: flex; justify-content: space-between; margin-bottom: 12px; gap: 8px; }
    .metric { display: flex; flex-direction: column; }
    .metric b { font-size: 1.25rem; color: var(--navy); line-height: 1.1; }
    .metric span { font-size: 0.75rem; color: #64748b; }
    .metric-good { color: #047857 !important; }
    .metric-bad { color: #b91c1c !important; }
    .metric-accent { color: #0284c7 !important; }
    .coverage-bar-track { height: 8px; background: #e2e8f0; border-radius: 99px; overflow: hidden; margin-bottom: 6px; }
    .coverage-bar-fill { height: 100%; background: var(--teal); border-radius: 99px; transition: width 0.3s; }
    .coverage-text { font-size: 0.82rem; color: #475569; margin: 0 0 16px; }
    .op-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: auto; }

    /* Tables */
    .table-card { padding: 22px; border-radius: 12px; }
    .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; gap: 12px; flex-wrap: wrap; }
    .table-header h3 { margin: 0; font-size: 1.2rem; color: var(--navy); }
    .filter-group { display: flex; align-items: center; gap: 10px; }
    .filter-group select { padding: 8px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 0.88rem; background: #fff; }
    .actions { display: flex; gap: 8px; align-items: center; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .data-table th { text-align: left; padding: 10px 14px; background: #f8fafc; color: #475569; font-weight: 700; border-bottom: 1px solid var(--line); }
    .data-table td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
    .sub-cell { display: block; font-size: 0.78rem; color: #64748b; margin-top: 2px; }
    .phone-link { color: #0369a1; text-decoration: none; font-weight: 600; font-family: monospace; }
    .phone-link:hover { text-decoration: underline; }
    .empty-cell { text-align: center; padding: 32px !important; color: #64748b; font-style: italic; }

    /* Badges & Chips */
    .badge { padding: 3px 8px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; display: inline-block; }
    .badge-complete { background: #dcfce7; color: #15803d; }
    .badge-partial { background: #fef9c3; color: #a16207; }
    .badge-empty { background: #fee2e2; color: #b91c1c; }
    .serial-pill { background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 99px; font-size: 0.82rem; }
    .category-chip { padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .category-chip[data-cat="SUPPORTER"] { background: #dcfce7; color: #15803d; }
    .category-chip[data-cat="SWING"] { background: #fef9c3; color: #a16207; }
    .category-chip[data-cat="OPPONENT"] { background: #fee2e2; color: #b91c1c; }
    .category-chip[data-cat="ABROAD"] { background: #f1f5f9; color: #64748b; }
    .toggle-pill { border: 1px solid var(--line); background: #f8fafc; border-radius: 99px; padding: 4px 12px; font-size: 0.78rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
    .toggle-pill.done { background: #dcfce7; border-color: #86efac; color: #166534; }
    .vote-status-btn { border: 1px solid var(--line); background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 0.78rem; font-weight: 700; cursor: pointer; }
    .vote-status-btn.voted { background: var(--teal); border-color: var(--teal); color: #fff; }

    /* Buttons */
    .btn-sm { padding: 6px 12px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; cursor: pointer; border: 1px solid transparent; }
    .btn-sm.outline { background: transparent; border-color: var(--line); color: var(--navy); }
    .btn-sm.outline:hover { background: #f1f5f9; }
    .btn-sm.highlight-btn { background: #0284c7; color: #fff; }
    .btn-sm.badge-btn { background: #4f46e5; color: #fff; }
    .btn-sm.form9-btn { background: #065f46; color: #fff; }
    .btn-sm.form8-btn { background: #047857; color: #fff; }
    .btn-sm.alert-btn { background: #dc2626; color: #fff; }
    .btn-sm.wa-pill-btn { background: #25d366; color: #fff; border-radius: 99px; padding: 4px 10px; font-size: 0.78rem; font-weight: 700; }
    .btn-sm.slip-pill-btn { background: #0f766e; color: #fff; border-radius: 99px; padding: 4px 10px; font-size: 0.78rem; font-weight: 700; }
    .btn-sm.danger { background: #fee2e2; color: #b91c1c; border-color: #fecaca; }
    .primary-button { background: var(--teal); color: #fff; border: none; padding: 9px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; }
    .primary-button:hover { background: #035f45; }
    .outline-btn { background: transparent; border: 1px solid var(--line); padding: 8px 14px; border-radius: 8px; font-weight: 600; cursor: pointer; color: var(--navy); }
    .text-button { background: transparent; border: none; padding: 8px 14px; cursor: pointer; color: #64748b; }
    .row-actions { display: flex; gap: 6px; align-items: center; }

    /* Avatars */
    .avatar-cell { width: 44px; height: 44px; border-radius: 8px; overflow: hidden; background: #f1f5f9; border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; }
    .agent-thumb { width: 100%; height: 100%; object-fit: cover; }
    .avatar-placeholder { font-size: 1.4rem; color: #94a3b8; }

    /* Modals */
    .modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.65); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 16px; }
    .modal-card { width: min(600px, 95vw); max-height: 90vh; overflow-y: auto; background: #fff; border-radius: 14px; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid var(--line); padding-bottom: 12px; }
    .modal-header h2 { margin: 0; font-size: 1.25rem; color: var(--navy); }
    .close-btn { background: transparent; border: none; font-size: 1.4rem; cursor: pointer; color: #64748b; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .form-field { display: flex; flex-direction: column; gap: 4px; }
    .form-field.wide { grid-column: 1 / -1; }
    .form-field label { font-size: 0.82rem; font-weight: 700; color: #334155; }
    .form-field input, .form-field select, .form-field textarea { padding: 9px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 0.88rem; font-family: inherit; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

    /* Pills & Target Filters */
    .target-pill { padding: 7px 12px; border-radius: 8px; border: 1px solid var(--line); background: #f8fafc; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.15s; }
    .target-pill.active-pill { background: #0284c7; color: #fff; border-color: #0284c7; font-weight: 700; }
    .tag-btn { background: #f1f5f9; color: #0369a1; border-color: #cbd5e1; font-size: 0.78rem; font-weight: 700; }
    .tag-btn:hover { background: #e0f2fe; }

    /* Incidents Workspace */
    .incidents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; margin-top: 18px; }
    .incident-card { border: 1px solid var(--line); border-radius: 12px; padding: 18px; background: #fff; display: flex; flex-direction: column; gap: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border-left: 5px solid #64748b; }
    .incident-card[data-severity="CRITICAL"] { border-left-color: #dc2626; background: #fffafa; }
    .incident-card[data-severity="HIGH"] { border-left-color: #ea580c; }
    .incident-card[data-severity="MEDIUM"] { border-left-color: #eab308; }
    .inc-head { display: flex; justify-content: space-between; align-items: center; }
    .severity-badge { font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 6px; background: #fef08a; color: #854d0e; text-transform: uppercase; }
    .severity-badge.crit { background: #fee2e2; color: #991b1b; }
    .inc-time { font-size: 0.75rem; color: #64748b; }
    .inc-title { margin: 0; font-size: 1.05rem; color: var(--navy); }
    .inc-desc { margin: 0; font-size: 0.88rem; color: #334155; line-height: 1.45; }
    .inc-meta-row { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; color: #475569; background: #f8fafc; padding: 8px 12px; border-radius: 6px; }
    .inc-footer { display: flex; justify-content: space-between; align-items: center; margin-top: auto; border-top: 1px solid #f1f5f9; padding-top: 12px; flex-wrap: wrap; gap: 8px; }
    .status-change-grp { display: flex; align-items: center; gap: 6px; font-size: 0.78rem; }
    .status-change-grp select { padding: 4px 8px; border-radius: 6px; border: 1px solid var(--line); font-size: 0.78rem; }
    .inc-actions { display: flex; gap: 6px; }
    .print-complaint-btn { background: #f8fafc; border: 1px solid #cbd5e1; font-size: 0.75rem; padding: 5px 10px; font-weight: 700; color: #dc2626; }

    /* ===================================================================== */
    /* PRINTABLE DOCUMENTS LAYOUT (Form-9, Badges, Batch IDs, Slips, etc.) */
    /* ===================================================================== */
    .print-preview-card { width: min(800px, 98vw); max-height: 92vh; overflow-y: auto; background: #f1f5f9; padding: 20px; }

    /* Form-9 Paper */
    .official-form9-paper { background: #fff; padding: 40px 48px; border: 1px solid #cbd5e1; box-shadow: 0 4px 18px rgba(0,0,0,0.06); font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.6; color: #000; max-width: 720px; margin: 0 auto; }
    .form9-header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px; }
    .gov-seal { font-size: 2.2rem; }
    .form9-title { margin: 4px 0 0; font-size: 1.5rem; }
    .form9-sub { margin: 0; font-size: 0.85rem; font-style: italic; }
    .form9-main-title { margin: 8px 0 0; font-size: 1.25rem; font-weight: 700; letter-spacing: 0.5px; }
    .form9-body { font-size: 0.95rem; }
    .recipient-line { margin: 0 0 16px; font-size: 1rem; }
    .paragraph-text { text-align: justify; margin-bottom: 16px; }
    .agent-spec-table { margin: 18px 0; border: 1px solid #000; padding: 8px 12px; }
    .agent-spec-table table { width: 100%; border-collapse: collapse; }
    .agent-spec-table td { padding: 4px 8px; font-size: 0.92rem; }
    .agent-spec-table .lbl { width: 40%; font-weight: 700; color: #222; }
    .declaration-block { background: #fafafa; border: 1px dashed #666; padding: 12px; margin: 18px 0; border-radius: 4px; font-size: 0.88rem; }
    .declaration-text { margin: 4px 0 0; }
    .signatures-row { display: flex; justify-content: space-between; margin-top: 48px; }
    .sig-col { text-align: center; width: 45%; }
    .sig-line { border-top: 1px solid #000; margin-bottom: 6px; }
    .sig-caption { margin: 2px 0 0; font-size: 0.78rem; color: #444; }
    .sig-symbol { margin: 2px 0 0; font-size: 0.85rem; font-weight: 700; }

    /* Single Agent Badge */
    .agent-badge-paper { background: #fff; width: 340px; margin: 0 auto; border: 2px solid #0e2942; border-radius: 10px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); font-family: sans-serif; }
    .badge-head { display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #0e2942; padding-bottom: 8px; margin-bottom: 12px; }
    .badge-emblem { font-size: 1.8rem; }
    .badge-org { margin: 0; font-size: 0.72rem; font-weight: 800; color: #0e2942; text-transform: uppercase; }
    .badge-type { margin: 0; font-size: 0.95rem; font-weight: 800; color: #047857; }
    .badge-symbol-hero { display: flex; align-items: center; gap: 10px; background: #ecfdf5; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; border: 1px solid #a7f3d0; }
    .badge-symbol-emoji { font-size: 2.2rem; line-height: 1; }
    .badge-cand-details { display: flex; flex-direction: column; }
    .badge-cand-name { font-size: 0.95rem; font-weight: 800; color: #064e3b; }
    .badge-symbol-txt { font-size: 0.78rem; color: #047857; font-weight: 700; }
    .badge-photo-id-row { display: flex; gap: 12px; margin-bottom: 12px; }
    .badge-photo-box { width: 85px; height: 105px; border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden; background: #f8fafc; display: flex; align-items: center; justify-content: center; }
    .badge-img { width: 100%; height: 100%; object-fit: cover; }
    .badge-placeholder { font-size: 0.72rem; color: #94a3b8; text-align: center; }
    .badge-bio { flex: 1; display: flex; flex-direction: column; gap: 4px; font-size: 0.82rem; }
    .badge-field { display: flex; flex-direction: column; }
    .badge-field .lbl { font-size: 0.68rem; color: #64748b; text-transform: uppercase; font-weight: 700; }
    .badge-field .val { color: #0f172a; }
    .badge-footer { border-top: 1px dashed #cbd5e1; padding-top: 8px; text-align: center; font-size: 0.68rem; color: #64748b; font-weight: 600; }

    /* Batch ID Cards (4 per page) */
    .batch-id-cards-page { background: #fff; padding: 14px; max-width: 860px; margin: 0 auto; }
    .batch-cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .official-agent-card { border: 2px solid #047857; border-radius: 12px; padding: 14px; background: #fff; display: flex; flex-direction: column; justify-content: space-between; page-break-inside: avoid; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
    .card-ec-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #047857; padding-bottom: 6px; margin-bottom: 8px; }
    .card-candidate-banner { display: flex; align-items: center; gap: 10px; background: #ecfdf5; border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; border: 1px solid #a7f3d0; }
    .card-symbol-badge { font-size: 2.2rem; line-height: 1; }
    .card-details-grid { display: grid; grid-template-columns: 80px 1fr 80px; gap: 10px; align-items: center; margin-bottom: 10px; }
    .card-photo-box { width: 80px; height: 95px; border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden; background: #f8fafc; }
    .photo-placeholder-box { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 1.4rem; color: #94a3b8; }
    .photo-placeholder-box small { font-size: 0.65rem; color: #64748b; }
    .card-info-col { display: flex; flex-direction: column; gap: 3px; font-size: 0.8rem; }
    .info-row { display: flex; flex-direction: column; }
    .info-k { font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
    .info-v { color: #0f172a; }
    .card-qr-box { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .card-ec-footer { border-top: 1px dashed #cbd5e1; padding-top: 6px; display: flex; justify-content: space-between; font-size: 0.65rem; color: #64748b; font-weight: 600; }

    /* Batch Voter Slips Print Paper */
    .wide-slip-modal { width: min(850px, 100%) !important; }
    .voter-slips-page { background: #fff; padding: 10px; }
    .voter-slips-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .voter-slip-card { border: 2px dashed #0e2942; border-radius: 10px; padding: 14px; background: #fff; display: flex; flex-direction: column; justify-content: space-between; page-break-inside: avoid; }
    .slip-header { display: flex; align-items: center; gap: 10px; border-bottom: 1.5px solid #0e2942; padding-bottom: 6px; margin-bottom: 6px; }
    .slip-symbol-emoji { font-size: 2rem; line-height: 1; }
    .slip-cand-info { display: flex; flex-direction: column; }
    .slip-cand-name { font-size: 1rem; color: #0e2942; }
    .slip-symbol-name { font-size: 0.78rem; color: var(--teal); font-weight: 800; }
    .slip-slogan { font-size: 0.75rem; font-style: italic; color: #475569; margin-bottom: 8px; text-align: center; border-bottom: 1px dotted #cbd5e1; padding-bottom: 4px; }
    .slip-body { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; }
    .slip-serial-row { display: flex; justify-content: space-between; align-items: center; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; }
    .slip-serial-num { font-size: 1.25rem; color: #0e2942; }
    .slip-row { display: flex; justify-content: space-between; padding: 2px 0; border-bottom: 1px solid #f8fafc; }
    .slip-row span { color: #64748b; }
    .slip-footer { font-size: 0.65rem; color: #475569; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 6px; margin-top: 8px; font-weight: 600; }

    /* Complaint Legal Paper */
    .official-complaint-paper { background: #fff; padding: 36px 40px; font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.6; color: #000; box-shadow: 0 4px 18px rgba(0,0,0,0.08); max-width: 750px; margin: 0 auto; }
    .complaint-head { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 18px; }
    .complaint-head h3 { margin: 4px 0 2px; font-size: 1.3rem; }
    .complaint-sub { margin: 0; font-size: 0.88rem; color: #333; }
    .complaint-date-ref { display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 16px; border-bottom: 1px dashed #999; padding-bottom: 6px; }
    .complaint-recipient { margin-bottom: 14px; font-size: 0.92rem; }
    .complaint-subject { margin-bottom: 16px; font-size: 0.95rem; border-left: 4px solid #000; padding-left: 10px; }
    .complaint-body-text { font-size: 0.92rem; text-align: justify; }
    .incident-statement-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; margin: 12px 0; font-size: 0.88rem; }
    .complaint-sig-row { display: flex; justify-content: space-between; margin-top: 50px; text-align: center; }
    .c-sig-block { width: 44%; }
    .c-sig-line { border-top: 1px solid #000; margin-bottom: 6px; }

    /* Form-8 Official Paper */
    .official-form8-paper { background: #fff; padding: 36px 40px; font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.55; color: #000; box-shadow: 0 4px 18px rgba(0,0,0,0.08); max-width: 760px; margin: 0 auto; }
    .form8-head { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 18px; }
    .form8-title { margin: 4px 0 0; font-size: 1.45rem; }
    .form8-rule { margin: 0; font-size: 0.85rem; font-style: italic; }
    .form8-main-title { margin: 8px 0 0; font-size: 1.25rem; font-weight: 700; }
    .form8-meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; font-size: 0.9rem; margin-bottom: 18px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 12px; }
    .form8-tally-table { width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: 0.92rem; }
    .form8-tally-table th, .form8-tally-table td { border: 1px solid #000; padding: 8px 10px; }
    .form8-tally-table th { background: #f1f5f9; text-align: left; }
    .form8-tally-table .highlight-row { background: #f0fdf4; font-weight: 600; }
    .form8-tally-table .total-row { background: #f8fafc; font-weight: 700; }
    .form8-sig-row { display: flex; justify-content: space-between; margin-top: 50px; text-align: center; }
    .f8-sig { width: 30%; }
    .f8-line { border-top: 1px solid #000; margin-bottom: 6px; }
    .f8-sig p { margin: 2px 0 0; font-size: 0.75rem; color: #444; }

    /* Print Overrides */
    @media print {
      body * { visibility: hidden !important; }
      .modal-backdrop, .modal-backdrop * { visibility: visible !important; }
      .modal-backdrop { position: absolute !important; inset: 0 !important; background: #fff !important; padding: 0 !important; }
      .modal-card { width: 100% !important; max-height: none !important; box-shadow: none !important; padding: 0 !important; border: none !important; }
      .official-form9-paper, .official-form9-paper *,
      .agent-badge-paper, .agent-badge-paper *,
      .batch-id-cards-page, .batch-id-cards-page *,
      .voter-slips-page, .voter-slips-page *,
      .digital-slip-card, .digital-slip-card *,
      .official-complaint-paper, .official-complaint-paper *,
      .official-form8-paper, .official-form8-paper * { visibility: visible !important; }
      .official-form9-paper, .agent-badge-paper, .batch-id-cards-page, .voter-slips-page, .official-complaint-paper, .official-form8-paper {
        position: absolute; left: 0; top: 0; width: 100%; margin: 0; padding: 15mm; border: none; box-shadow: none;
      }
      .batch-cards-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 15mm 10mm !important; }
      .official-agent-card { page-break-inside: avoid !important; }
      .voter-slips-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 10mm !important; }
      .voter-slip-card { page-break-inside: avoid !important; }
      .no-print { display: none !important; }
    }
'''

