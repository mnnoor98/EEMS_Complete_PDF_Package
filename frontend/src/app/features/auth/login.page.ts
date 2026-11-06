import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'eems-login',
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
<main class="login-shell">
  <section class="brand-panel">
    <div class="brand"><span>E</span> EEMS</div>
    <div>
      <p class="eyebrow light">Election operations platform</p>
      <h1>Run every field operation from one trusted workspace.</h1>
      <p class="lead">নির্বাচন, টিম, কেন্দ্র, প্রশিক্ষণ এবং মাঠপর্যায়ের কাজ নিরাপদে পরিচালনা করুন।</p>
    </div>
    <p class="boundary">Administrative operations only. No voter profiling or persuasion targeting.</p>
  </section>

  <section class="form-panel">
    <form [formGroup]="form" (ngSubmit)="submit()" class="login-card">
      <div>
        <p class="eyebrow">Secure access</p>
        <h2>Welcome back</h2>
        <p>Sign in to your tenant workspace.</p>
      </div>

      @if(error()){
        <div class="error-banner" role="alert">{{error()}}</div>
      }

      <div class="demo-badge-card">
        <div class="demo-top">
          <b>🔑 Demo Credentials</b>
          <button type="button" class="chip-btn" (click)="fillAdmin()">Auto-Fill Admin</button>
        </div>
        <div class="demo-chips">
          <span>Tenant: <code>1000000000</code></span>
          <span>User: <code>admin</code></span>
          <span>Pass: <code>EEMS&#64;123456!</code></span>
        </div>
      </div>

      <div class="form-field">
        <label for="tenant">Tenant ID <small>(10-digit Organization Code)</small></label>
        <input
          id="tenant"
          formControlName="tenantId"
          autocomplete="organization"
          inputmode="numeric"
          maxlength="10"
          placeholder="1000000000"
        />
        @if(form.controls.tenantId.touched && form.controls.tenantId.errors?.['pattern']){
          <span class="field-error">Tenant ID must be exactly 10 digits (e.g. 1000000000).</span>
        }
      </div>

      <div class="form-field">
        <label for="username">Username</label>
        <input
          id="username"
          formControlName="username"
          autocomplete="username"
          placeholder="admin"
        />
      </div>

      <div class="form-field">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          formControlName="password"
          autocomplete="current-password"
          placeholder="••••••••••••"
        />
      </div>

      <button class="primary-button" [disabled]="form.invalid || busy()">
        {{busy() ? 'Signing in...' : 'Sign in securely'}}
      </button>

      <small>Access is permission-controlled and security events are audited.</small>
    </form>
  </section>
</main>
`,
  styles: [`
.login-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(360px, 1.05fr) minmax(360px, 0.95fr);
}
.brand-panel {
  background: linear-gradient(145deg, #0e2942, #17395b 62%, #156b7d);
  color: #fff;
  padding: clamp(32px, 6vw, 84px);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}
.brand-panel:after {
  content: '';
  position: absolute;
  width: 420px;
  height: 420px;
  border: 1px solid rgba(255, 255, 255, 0.13);
  border-radius: 50%;
  right: -170px;
  top: 16%;
}
.brand {
  font-weight: 800;
  font-size: 1.2rem;
  letter-spacing: 0.08em;
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand span {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 11px;
  background: var(--mint);
}
h1 {
  font-size: clamp(2.2rem, 5vw, 4.8rem);
  line-height: 1.02;
  letter-spacing: -0.055em;
  max-width: 790px;
  margin: 14px 0;
}
.lead {
  max-width: 620px;
  font-size: 1.12rem;
  color: #d8e8ef;
}
.light {
  color: #82ddd5;
}
.boundary {
  font-size: 0.75rem;
  color: #b8cdd8;
}
.form-panel {
  display: grid;
  place-items: center;
  padding: 28px;
}
.login-card {
  width: min(440px, 100%);
  display: grid;
  gap: 20px;
}
.login-card h2 {
  font-size: 2rem;
  margin: 5px 0;
}
.login-card p {
  color: var(--muted);
  margin: 0;
}
.login-card small {
  color: var(--muted);
  text-align: center;
}
.demo-badge-card {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 12px 14px;
  display: grid;
  gap: 8px;
}
.demo-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #166534;
}
.chip-btn {
  background: #166534;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s;
}
.chip-btn:hover {
  opacity: 0.9;
}
.demo-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.75rem;
  color: #15803d;
}
.demo-chips code {
  background: #dcfce7;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
  color: #14532d;
}
.form-field {
  display: grid;
  gap: 6px;
}
.form-field label {
  font-size: 0.78rem;
  font-weight: 700;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form-field label small {
  font-weight: 400;
  color: var(--muted);
}
.form-field input {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.95rem;
}
.field-error {
  color: #b91c1c;
  font-size: 0.72rem;
  font-weight: 600;
}
.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
}
@media (max-width: 800px) {
  .login-shell {
    grid-template-columns: 1fr;
  }
  .brand-panel {
    min-height: 280px;
    padding: 28px;
  }
  .brand-panel h1 {
    font-size: 2.4rem;
  }
  .boundary {
    display: none;
  }
  .form-panel {
    padding: 40px 22px;
  }
}
`]
})
export class LoginPage {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly busy = signal(false);
  readonly error = signal('');

  readonly form = this.fb.nonNullable.group({
    tenantId: ['1000000000', [Validators.required, Validators.pattern(/^\d{10}$/)]],
    username: ['admin', Validators.required],
    password: ['EEMS@123456!', Validators.required]
  });

  fillAdmin() {
    this.form.patchValue({
      tenantId: '1000000000',
      username: 'admin',
      password: 'EEMS@123456!'
    });
  }

  submit() {
    if (this.form.invalid) return;
    this.busy.set(true);
    this.error.set('');
    const value = this.form.getRawValue();
    this.auth.login(value.tenantId, value.username, value.password).subscribe({
      next: result => {
        if (result.passwordChangeRequired) {
          void this.router.navigateByUrl('/change-password');
        } else if (!result.isSuperAdmin && result.candidateId) {
          const electId = result.candidateElectionId || '7a2ec4ed-9aba-4707-aa49-a58b51e82713';
          void this.router.navigateByUrl(`/elections/${electId}/candidate-war-room`);
        } else {
          void this.router.navigateByUrl('/dashboard');
        }
      },
      error: (err: { status?: number }) => {
        this.busy.set(false);
        if (err.status === 400) {
          this.error.set('Validation failed: Tenant ID must be exactly 10 digits.');
        } else if (err.status === 401) {
          this.error.set('Sign-in failed. Check Tenant ID (1000000000), username, or password.');
        } else if (err.status === 429) {
          this.error.set('Too many login attempts. Please wait 1 minute before trying again.');
        } else {
          this.error.set('Unable to connect to the backend server. Verify http://localhost:5131 is running.');
        }
      }
    });
  }
}
