# -*- coding: utf-8 -*-
file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

f8_methods = """
  // =========================================================================
  // FORM-8 & WINNER CONSOLIDATION CERTIFICATE METHODS
  // =========================================================================
  openForm8Modal(center: CandidateCenterResultItem) {
    this.selectedCenterForForm8.set(center);
    this.form8UploadData.set('');
    this.form8FileName.set('');
    this.form8PreviewUrl.set(center.form8DocumentUrl || '');
    this.form8PresidingOfficer = center.presidingOfficerName || '';
    this.form8Phone = center.presidingOfficerPhone || '';
    this.form8CancelledVotes = center.cancelledVotes || 0;
    this.form8Note = center.verificationNote || '';
    this.form8Verified = true;
    this.showForm8Modal.set(true);
  }

  closeForm8Modal() {
    this.showForm8Modal.set(false);
    this.selectedCenterForForm8.set(null);
  }

  onForm8FileSelected(event: any) {
    const file = event.target?.files?.[0];
    if (!file) return;
    this.form8FileName.set(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      this.form8UploadData.set(result);
      this.form8PreviewUrl.set(result);
    };
    reader.readAsDataURL(file);
  }

  submitForm8() {
    const center = this.selectedCenterForForm8();
    if (!center) return;
    if (!this.form8UploadData() && !center.form8DocumentUrl) {
      alert('অনুগ্রহ করে প্রিজাইডিং অফিসারের স্বাক্ষরিত ফরম-৮ এর ছবি বা স্ক্যান কপি সিলেক্ট করুন।');
      return;
    }

    this.form8Uploading.set(true);
    const req: UploadAndVerifyForm8Request = {
      documentData: this.form8UploadData() || 'EXISTING',
      fileName: this.form8FileName() || 'form8_result_sheet.jpg',
      presidingOfficerName: this.form8PresidingOfficer,
      presidingOfficerPhone: this.form8Phone,
      cancelledVotes: Number(this.form8CancelledVotes) || 0,
      isVerified: this.form8Verified,
      verificationNote: this.form8Note
    };

    this.api.uploadForm8(this.electionId, center.electionCenterId, req).subscribe({
      next: () => {
        this.form8Uploading.set(false);
        this.closeForm8Modal();
        this.loadResultsSummary();
        alert('ফরম-৮ সফলভাবে আপলোড ও অফিসিয়াল ভেরিফিকেশন সম্পন্ন হয়েছে।');
      },
      error: err => {
        this.form8Uploading.set(false);
        const detail = err?.error?.message || err?.error?.error || err?.message || 'ফরম-৮ আপলোড করা সম্ভব হয়নি।';
        alert(`ত্রুটি: ${detail}`);
      }
    });
  }

  openWinnerCertificateModal() {
    this.showWinnerCertificateModal.set(true);
  }

  closeWinnerCertificateModal() {
    this.showWinnerCertificateModal.set(false);
  }

  printCertificate() {
    window.print();
  }

  openForm8StatementModal(center: CandidateCenterResultItem) {
    this.selectedCenterForForm8Statement.set(center);
  }

  closeForm8StatementModal() {
    this.selectedCenterForForm8Statement.set(null);
  }

  calcTotalValidVotes(cr?: CandidateCenterResultItem | null): number {
    if (!cr) return 0;
    if (cr.candidateVotesList && cr.candidateVotesList.length > 0) {
      return cr.candidateVotesList.reduce((acc, v) => acc + (v.votes || 0), 0);
    }
    return (cr.candidateVotes || 0) + (cr.runnerUpVotes || 0);
  }

  calcTotalCastVotes(cr?: CandidateCenterResultItem | null): number {
    if (!cr) return 0;
    return this.calcTotalValidVotes(cr) + (cr.cancelledVotes || 0);
  }

  numberToBanglaWords(num?: number | null): string {
    if (!num || num === 0) return 'শূন্য';
    const ones = ['', 'এক', 'দুই', 'তিন', 'চার', 'পাঁচ', 'ছয়', 'সাত', 'আট', 'নয়', 'দশ',
      'এগারো', 'বারো', 'তেরো', 'চৌদ্দ', 'পনেরো', 'ষোল', 'সতেরো', 'আঠারো', 'উনিশ', 'বিশ',
      'একুশ', 'বাইশ', 'তেইশ', 'চব্বিশ', 'পঁচিশ', 'ছাব্বিশ', 'সাতাশ', 'আঠাশ', 'ঊনত্রিশ', 'ত্রিশ',
      'একত্রিশ', 'বত্রিশ', 'তেত্রিশ', 'চৌত্রিশ', 'পঁয়ত্রিশ', 'ছত্রিশ', 'সাঁইত্রিশ', 'আটত্রিশ', 'ঊনচল্লিশ', 'চল্লিশ',
      'একচল্লিশ', 'বিয়াল্লিশ', 'তেতাল্লিশ', 'চুয়াল্লিশ', 'পঁয়তাল্লিশ', 'ছেচল্লিশ', 'সাতচল্লিশ', 'আটচল্লিশ', 'ঊনপঞ্চাশ', 'পঞ্চাশ',
      'একান্ন', 'বায়ান্ন', 'তিপ্পান্ন', 'চুয়াল্লান্ন', 'পঞ্চান্ন', 'ছাপ্পান্ন', 'সাতান্ন', 'আটান্ন', 'ঊনষাট', 'ষাট',
      'একষট্টি', 'বাষট্টি', 'তেষট্টি', 'চৌষট্টি', 'পঁয়ষট্টি', 'ছেষট্টি', 'সাতষট্টি', 'আটষট্টি', 'ঊনসত্তর', 'সত্তর',
      'একাত্তর', 'বাহাত্তর', 'তিয়াত্তর', 'চুয়াত্তর', 'পঁচাত্তর', 'ছিয়াত্তর', 'সাতাত্তর', 'আটাত্তর', 'ঊনআশি', 'আশি',
      'একাশি', 'বিরাশি', 'তিরাশি', 'চুরাশি', 'পঁচাশি', 'ছিয়াশি', 'সাতাশি', 'অষ্টআশি', 'ঊননব্বই', 'নব্বই',
      'একানব্বই', 'বিরানব্বই', 'তিরানব্বই', 'চুরানব্বই', 'পঁচানব্বই', 'ছিয়ানব্বই', 'সাতানব্বই', 'আটানব্বই', 'নিরানব্বই'];

    const convertChunk = (n: number): string => {
      let str = '';
      const crore = Math.floor(n / 10000000);
      n %= 10000000;
      const lakh = Math.floor(n / 100000);
      n %= 100000;
      const thousand = Math.floor(n / 1000);
      n %= 1000;
      const hundred = Math.floor(n / 100);
      const rest = n % 100;

      if (crore > 0) str += convertChunk(crore) + ' কোটি ';
      if (lakh > 0) str += ones[lakh] + ' লাখ ';
      if (thousand > 0) str += ones[thousand] + ' হাজার ';
      if (hundred > 0) str += ones[hundred] + ' শত ';
      if (rest > 0) str += ones[rest] + ' ';
      return str.trim();
    };

    return convertChunk(num);
  }
"""

anchor = "  // =========================================================================\n  // VOTERS MANAGEMENT METHODS"

if "openForm8StatementModal(center:" not in content and anchor in content:
    content = content.replace(anchor, f8_methods + "\n" + anchor, 1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Form8 methods injected cleanly.")
else:
    print("WARN: anchor not found or openForm8StatementModal already in file.")
