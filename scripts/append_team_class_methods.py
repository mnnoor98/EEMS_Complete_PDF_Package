with open('scripts/war_room_blocks/block4_class.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Signals to add
signal_anchor = '  showVoterBroadcastModal = signal(false);'
new_signals = '''  // Team & Sub-Users Signals
  teamUsers = signal<any[]>([]);
  loadingTeamUsers = signal(false);
  showCreateTeamUserModal = signal(false);
  savingTeamUser = signal(false);
  newTeamUser = {
    username: '',
    displayName: '',
    phone: '',
    email: '',
    password: '',
    role: 'ক্যাম্পেইন সমন্বয়ক'
  };
  showResetPasswordModal = signal(false);
  selectedUserForReset = signal<any>(null);
  resetNewPassword = '';
  savingResetPassword = signal(false);

  showVoterBroadcastModal = signal(false);'''

assert signal_anchor in text, "signal_anchor not found"
text = text.replace(signal_anchor, new_signals, 1)

# 2. In ngOnInit, call loadTeamUsers
ng_init_anchor = '    this.loadIncidents();'
new_ng_init = '''    this.loadIncidents();
    this.loadTeamUsers();'''

assert ng_init_anchor in text, "ng_init_anchor not found"
text = text.replace(ng_init_anchor, new_ng_init, 1)

# 3. Add methods before closing bracket
team_methods = '''
  // =========================================================================
  // TEAM & SUB-USERS METHODS
  // =========================================================================

  loadTeamUsers() {
    this.loadingTeamUsers.set(true);
    this.api.getCandidateTeamUsers(this.candidateId).subscribe({
      next: users => {
        this.loadingTeamUsers.set(false);
        this.teamUsers.set(users || []);
      },
      error: () => this.loadingTeamUsers.set(false)
    });
  }

  openCreateTeamUserModal() {
    this.newTeamUser = {
      username: '',
      displayName: '',
      phone: '',
      email: '',
      password: '',
      role: 'ক্যাম্পেইন সমন্বয়ক'
    };
    this.showCreateTeamUserModal.set(true);
  }

  closeCreateTeamUserModal() {
    this.showCreateTeamUserModal.set(false);
  }

  submitCreateTeamUser() {
    if (!this.newTeamUser.username || !this.newTeamUser.displayName || !this.newTeamUser.password) {
      alert('অনুগ্রহ করে নাম, ব্যবহারকারী আইডি এবং পাসওয়ার্ড পূরণ করুন।');
      return;
    }
    if (this.newTeamUser.password.length < 6) {
      alert('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।');
      return;
    }

    this.savingTeamUser.set(true);
    this.api.createCandidateTeamUser({
      ...this.newTeamUser,
      candidateId: this.candidateId
    }).subscribe({
      next: res => {
        this.savingTeamUser.set(false);
        this.closeCreateTeamUserModal();
        this.loadTeamUsers();
        alert(`✅ ক্যাম্পেইন কর্মী '${res.displayName}' (${res.username}) সফলভাবে তৈরি ও সক্রিয় করা হয়েছে!`);
      },
      error: err => {
        this.savingTeamUser.set(false);
        alert(err?.error?.message || 'কর্মী অ্যাকাউন্ট তৈরি করতে ব্যর্থ হয়েছে। অন্য ইউজারনেম দিয়ে চেষ্টা করুন।');
      }
    });
  }

  toggleTeamUserStatus(user: any) {
    const action = user.isActive ? 'নিষ্ক্রিয়' : 'সক্রিয়';
    if (!confirm(`আপনি কি নিশ্চিত যে '${user.displayName}' অ্যাকাউন্টটি ${action} করতে চান?`)) return;

    this.api.toggleCandidateTeamUserStatus(user.userId, !user.isActive).subscribe({
      next: () => {
        this.loadTeamUsers();
        alert(`ব্যবহারকারী সফলভাবে ${action} করা হয়েছে।`);
      },
      error: () => alert('স্ট্যাটাস পরিবর্তন ব্যর্থ হয়েছে।')
    });
  }

  openResetPasswordModal(user: any) {
    this.selectedUserForReset.set(user);
    this.resetNewPassword = '';
    this.showResetPasswordModal.set(true);
  }

  closeResetPasswordModal() {
    this.showResetPasswordModal.set(false);
    this.selectedUserForReset.set(null);
  }

  submitResetPassword() {
    const user = this.selectedUserForReset();
    if (!user || !this.resetNewPassword) return;
    if (this.resetNewPassword.length < 6) {
      alert('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।');
      return;
    }

    this.savingResetPassword.set(true);
    this.api.resetCandidateTeamUserPassword(user.userId, this.resetNewPassword).subscribe({
      next: () => {
        this.savingResetPassword.set(false);
        this.closeResetPasswordModal();
        alert(`✅ '${user.displayName}'-এর পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে!`);
      },
      error: () => {
        this.savingResetPassword.set(false);
        alert('পাসওয়ার্ড পরিবর্তন করতে ব্যর্থ হয়েছে।');
      }
    });
  }
}
'''

# Find the last '}' of the class
last_brace_pos = text.rfind('}')
assert last_brace_pos != -1, "closing brace not found"

new_text = text[:last_brace_pos] + team_methods

with open('scripts/war_room_blocks/block4_class.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Appended team methods to block4_class.py successfully!')

