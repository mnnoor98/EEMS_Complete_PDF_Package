import { ChangeDetectionStrategy, Component, inject, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Observable } from 'rxjs';
import { EemsApiService } from '../../core/api/eems-api.service';
import { MasterDataWorkspace } from '../../core/models/api.models';

@Component({
  selector: 'eems-master-data',
  imports: [FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
<nav><a routerLink="/administration">Administration</a><span>/</span><b>Master data</b></nav>
<header>
  <div>
    <p class="eyebrow">SYSTEM CONFIGURATION</p>
    <h1 class="page-title">Master data management</h1>
    <p>Maintain controlled reference values used across elections, field operations, and geographic administrative hierarchies.</p>
  </div>
  <button class="outline" (click)="load()">Refresh</button>
</header>

@if(error()){<div class="error-banner">{{error()}}</div>}
@if(notice()){<div class="success-banner">{{notice()}}</div>}

<section class="tabs">
  @for(item of tabs;track item.key){
    <button [class.active]="tab()===item.key" (click)="selectTab(item.key)">
      {{item.label}} <b>{{count(item.key)}}</b>
    </button>
  }
</section>

@if(loading()){
  <div class="card empty">Loading master data…</div>
} @else {
  <section class="workspace">
    <article class="card form-card">
      <p class="eyebrow">NEW REFERENCE</p>
      <h2>Add {{tabLabel()}}</h2>

      @switch(tab()){
        @case('areas'){
          <form (ngSubmit)="addArea()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="areaId" readonly [ngModel]="area.id" class="readonly-id">
            </label>
            <label>Code
              <input name="areaCode" required maxlength="40" [(ngModel)]="area.code" placeholder="e.g. DHAKA-NORTH">
            </label>
            <label>Area type
              <select name="areaType" required [(ngModel)]="area.areaTypeId">
                <option [ngValue]="0">Select type</option>
                @for(x of data().areaTypes;track x.id){<option [ngValue]="x.id">{{x.name}} (Level {{x.level}})</option>}
              </select>
            </label>
            <label>Parent area
              <select name="parent" [(ngModel)]="area.parentAreaId">
                <option [ngValue]="null">No parent (Top level)</option>
                @for(x of data().areas;track x.id){<option [ngValue]="x.id">{{x.nameEn||x.nameBn}} · {{x.code}}</option>}
              </select>
            </label>
            <label>Bangla name
              <input name="nameBn" required maxlength="200" [(ngModel)]="area.nameBn" placeholder="বাংলা নাম">
            </label>
            <label>English name
              <input name="nameEn" maxlength="200" [(ngModel)]="area.nameEn" placeholder="English name (optional)">
            </label>
            <button class="primary-button" [disabled]="saving()||!validArea()">Add area</button>
          </form>
        }

        @case('areaTypes'){
          <form (ngSubmit)="addAreaType()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="atId" readonly [ngModel]="areaType.id" class="readonly-id">
            </label>
            <label>Code
              <input name="atCode" required maxlength="40" [(ngModel)]="areaType.code" placeholder="e.g. MUNICIPALITY">
            </label>
            <label>Name
              <input name="atName" required maxlength="120" [(ngModel)]="areaType.name" placeholder="e.g. Municipality / Pouroshava">
            </label>
            <label>Hierarchy Level
              <input type="number" min="1" max="10" name="atLevel" required [(ngModel)]="areaType.level" placeholder="e.g. 6">
            </label>
            <button class="primary-button" [disabled]="saving()||!validAreaType()">Add area type</button>
          </form>
        }

        @case('electionTypes'){
          <form (ngSubmit)="addElectionType()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="etId" readonly [ngModel]="electionType.id" class="readonly-id">
            </label>
            <label>Code
              <input name="etCode" required maxlength="40" [(ngModel)]="electionType.code" placeholder="e.g. PARLIAMENTARY">
            </label>
            <label>Name
              <input name="etName" required maxlength="120" [(ngModel)]="electionType.name" placeholder="e.g. General Parliamentary Election">
            </label>
            <button class="primary-button" [disabled]="saving()||!validSimple(electionType)">Add election type</button>
          </form>
        }

        @case('lifecycleStates'){
          <form (ngSubmit)="addLifecycleState()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="lsId" readonly [ngModel]="lifecycleState.id" class="readonly-id">
            </label>
            <label>Code
              <input name="lsCode" required maxlength="40" [(ngModel)]="lifecycleState.code" placeholder="e.g. POST_ELECTION">
            </label>
            <label>Name
              <input name="lsName" required maxlength="100" [(ngModel)]="lifecycleState.name" placeholder="e.g. Post-Election Review">
            </label>
            <label class="check">
              <input type="checkbox" name="lsTerminal" [(ngModel)]="lifecycleState.isTerminal"> Terminal state (Closed/Archived)
            </label>
            <button class="primary-button" [disabled]="saving()||!validSimple(lifecycleState)">Add lifecycle state</button>
          </form>
        }

        @case('positions'){
          <form (ngSubmit)="addPosition()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="pId" readonly [ngModel]="position.id" class="readonly-id">
            </label>
            <label>Election type
              <select name="pType" [(ngModel)]="position.electionTypeId">
                <option [ngValue]="0">Select election type</option>
                @for(x of data().electionTypes;track x.id){<option [ngValue]="x.id">{{x.name}}</option>}
              </select>
            </label>
            <label>Code
              <input name="pCode" required maxlength="60" [(ngModel)]="position.code" placeholder="e.g. MP">
            </label>
            <label>Name
              <input name="pName" required maxlength="120" [(ngModel)]="position.name" placeholder="e.g. Member of Parliament">
            </label>
            <button class="primary-button" [disabled]="saving()||!validPosition()">Add position</button>
          </form>
        }

        @case('taskStates'){
          <form (ngSubmit)="addTaskState()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="sId" readonly [ngModel]="taskState.id" class="readonly-id">
            </label>
            <label>Code
              <input name="sCode" required maxlength="40" [(ngModel)]="taskState.code" placeholder="e.g. IN_PROGRESS">
            </label>
            <label>Name
              <input name="sName" required maxlength="100" [(ngModel)]="taskState.name" placeholder="e.g. In Progress">
            </label>
            <label class="check">
              <input type="checkbox" name="terminal" [(ngModel)]="taskState.isTerminal"> Terminal state (Closed/Completed)
            </label>
            <button class="primary-button" [disabled]="saving()||!validSimple(taskState)">Add task state</button>
          </form>
        }

        @case('taskPriorities'){
          <form (ngSubmit)="addTaskPriority()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="prId" readonly [ngModel]="taskPriority.id" class="readonly-id">
            </label>
            <label>Rank
              <input type="number" min="1" name="rank" required [(ngModel)]="taskPriority.rank" placeholder="e.g. 1">
            </label>
            <label>Code
              <input name="prCode" required maxlength="40" [(ngModel)]="taskPriority.code" placeholder="e.g. CRITICAL">
            </label>
            <label>Name
              <input name="prName" required maxlength="100" [(ngModel)]="taskPriority.name" placeholder="e.g. Critical Priority">
            </label>
            <button class="primary-button" [disabled]="saving()||!validPriority()">Add priority</button>
          </form>
        }

        @case('eventTypes'){
          <form (ngSubmit)="addEventType()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="evId" readonly [ngModel]="eventType.id" class="readonly-id">
            </label>
            <label>Code
              <input name="evCode" required maxlength="40" [(ngModel)]="eventType.code" placeholder="e.g. PRESS_BRIEFING">
            </label>
            <label>Name
              <input name="evName" required maxlength="100" [(ngModel)]="eventType.name" placeholder="e.g. Press Briefing">
            </label>
            <button class="primary-button" [disabled]="saving()||!validSimple(eventType)">Add event type</button>
          </form>
        }

        @case('movementTypes'){
          <form (ngSubmit)="addMovementType()">
            <label>Numeric ID <span class="auto-badge">Auto</span>
              <input type="number" name="mvId" readonly [ngModel]="movementType.id" class="readonly-id">
            </label>
            <label>Code
              <input name="mvCode" required maxlength="40" [(ngModel)]="movementType.code" placeholder="e.g. RETURN">
            </label>
            <label>Name
              <input name="mvName" required maxlength="100" [(ngModel)]="movementType.name" placeholder="e.g. Return to Central Store">
            </label>
            <label class="check">
              <input type="checkbox" name="mvSrc" [(ngModel)]="movementType.requiresSource"> Requires source warehouse
            </label>
            <label class="check">
              <input type="checkbox" name="mvDst" [(ngModel)]="movementType.requiresDestination"> Requires destination warehouse
            </label>
            <button class="primary-button" [disabled]="saving()||!validMovementType()">Add movement type</button>
          </form>
        }
      }
    </article>

    <article class="card directory">
      <header>
        <div>
          <p class="eyebrow">REFERENCE DIRECTORY</p>
          <h2>{{tabLabel()}}</h2>
        </div>
        <span>{{count(tab())}} records</span>
      </header>

      @if(tab() === 'areas'){
        <div class="filter-bar">
          <input [(ngModel)]="areaSearch" placeholder="Filter areas (name or code)..." class="filter-input">
          <select [(ngModel)]="areaTypeFilter" class="filter-select">
            <option [ngValue]="0">All area types</option>
            @for(t of data().areaTypes; track t.id){
              <option [ngValue]="t.id">{{t.name}}</option>
            }
          </select>
        </div>
      }

      <div class="table">
        @switch(tab()){
          @case('areas'){
            @for(x of filteredAreas(); track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.nameEn || x.nameBn}} <small class="bn-text">({{x.nameBn}})</small></b>
                <small>{{areaTypeName(x.areaTypeId)}} · ID {{x.id}}</small>
                <i>{{x.isActive ? 'Active' : 'Inactive'}}</i>
              </div>
            }
            @if(!filteredAreas().length){
              <div class="empty-hint">No matching areas found.</div>
            }
          }
          @case('areaTypes'){
            @for(x of data().areaTypes; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>ID {{x.id}}</small>
                <i>Level {{x.level}}</i>
              </div>
            }
          }
          @case('electionTypes'){
            @for(x of data().electionTypes; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>ID {{x.id}}</small>
                <i>Active</i>
              </div>
            }
          }
          @case('lifecycleStates'){
            @for(x of data().lifecycleStates ?? []; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>ID {{x.id}}</small>
                <i>{{x.isTerminal ? 'Terminal' : 'Active'}}</i>
              </div>
            }
          }
          @case('positions'){
            @for(x of data().positions; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>{{electionTypeName(x.electionTypeId)}} · ID {{x.id}}</small>
                <i>Active</i>
              </div>
            }
          }
          @case('taskStates'){
            @for(x of data().taskStates; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>ID {{x.id}}</small>
                <i>{{x.isTerminal ? 'Terminal' : 'Open'}}</i>
              </div>
            }
          }
          @case('taskPriorities'){
            @for(x of data().taskPriorities; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>ID {{x.id}}</small>
                <i>Rank {{x.rank}}</i>
              </div>
            }
          }
          @case('eventTypes'){
            @for(x of data().eventTypes ?? []; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>ID {{x.id}}</small>
                <i>Active</i>
              </div>
            }
          }
          @case('movementTypes'){
            @for(x of data().movementTypes ?? []; track x.id){
              <div>
                <code>{{x.code}}</code>
                <b>{{x.name}}</b>
                <small>ID {{x.id}}</small>
                <i>{{x.requiresSource ? 'Source' : ''}} {{x.requiresDestination ? '→ Dest' : ''}}</i>
              </div>
            }
          }
        }
      </div>
    </article>
  </section>
}
`,
  styles: [`
:host { display: block; }
nav { display: flex; gap: 8px; font-size: 0.75rem; color: var(--muted); margin-bottom: 18px; }
nav a { color: var(--teal); text-decoration: none; }
header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 18px; }
header p { margin-bottom: 0; color: var(--muted); }
.outline { border: 1px solid var(--line); background: white; padding: 9px 12px; border-radius: 9px; font-weight: 700; cursor: pointer; }
.tabs { display: flex; gap: 7px; overflow: auto; margin-bottom: 14px; padding-bottom: 4px; }
.tabs button { border: 1px solid var(--line); background: white; border-radius: 9px; padding: 10px 13px; white-space: nowrap; font-weight: 700; cursor: pointer; }
.tabs button.active { background: var(--navy); color: white; border-color: var(--navy); }
.tabs b { margin-left: 5px; opacity: 0.8; font-size: 0.82rem; }
.workspace { display: grid; grid-template-columns: 360px 1fr; gap: 14px; }
.form-card, .directory { padding: 20px; }
.form-card h2, .directory h2 { margin: 3px 0; }
.form-card form { display: grid; gap: 13px; margin-top: 18px; }
.form-card label { display: grid; gap: 6px; font-size: 0.74rem; font-weight: 700; }
.form-card input, .form-card select { border: 1px solid var(--line); border-radius: 8px; padding: 10px; font-size: 0.9rem; }
.readonly-id { background: #f1f5f9; color: #334155; font-weight: 800; cursor: not-allowed; border-color: #cbd5e1; }
.auto-badge { font-size: 0.65rem; color: #0e7490; background: #e0f2fe; padding: 2px 7px; border-radius: 99px; margin-left: 6px; text-transform: uppercase; font-weight: 800; letter-spacing: 0.04em; display: inline-block; width: fit-content; }
.form-card .check { display: flex; align-items: center; gap: 8px; font-weight: 600; cursor: pointer; }
.form-card .check input { width: auto; }
.directory header { border-bottom: 1px solid var(--line); padding-bottom: 13px; }
.directory header span { font-size: 0.72rem; color: var(--muted); }
.filter-bar { display: grid; grid-template-columns: 1fr 180px; gap: 10px; margin-top: 14px; margin-bottom: 10px; }
.filter-input, .filter-select { border: 1px solid var(--line); border-radius: 8px; padding: 8px 12px; font-size: 0.82rem; }
.table { max-height: 560px; overflow-y: auto; }
.table > div { display: grid; grid-template-columns: 140px 1.4fr 1fr auto; gap: 12px; align-items: center; padding: 11px 4px; border-bottom: 1px solid var(--line); }
code { color: var(--teal); font-weight: 800; font-size: 0.8rem; }
.bn-text { font-weight: 400; color: #64748b; margin-left: 4px; }
.table small { color: var(--muted); font-size: 0.76rem; }
.table i { font-style: normal; font-size: 0.68rem; background: #edf5f3; color: #176d65; padding: 4px 8px; border-radius: 99px; white-space: nowrap; }
.success-banner { border: 1px solid #a8ddd1; background: #effbf8; color: #126b64; padding: 12px; border-radius: 9px; margin-bottom: 12px; font-weight: 600; }
.error-banner { border: 1px solid #fecaca; background: #fef2f2; color: #991b1b; padding: 12px; border-radius: 9px; margin-bottom: 12px; font-weight: 600; }
.empty { min-height: 180px; display: grid; place-items: center; }
.empty-hint { padding: 24px; text-align: center; color: var(--muted); }
@media (max-width: 900px) {
  .workspace { grid-template-columns: 1fr; }
  .table > div { grid-template-columns: 90px 1fr; }
  .table small, .table i { grid-column: 2; }
  .filter-bar { grid-template-columns: 1fr; }
}
`]
})
export class MasterDataPage {
  private api = inject(EemsApiService);

  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal('');
  readonly notice = signal('');
  readonly tab = signal('areas');

  areaSearch = '';
  areaTypeFilter = 0;

  readonly data = signal<MasterDataWorkspace>({
    areaTypes: [],
    areas: [],
    electionTypes: [],
    lifecycleStates: [],
    positions: [],
    taskStates: [],
    taskPriorities: [],
    eventTypes: [],
    movementTypes: []
  });

  readonly tabs = [
    { key: 'areas', label: 'Geographic areas' },
    { key: 'areaTypes', label: 'Area types' },
    { key: 'electionTypes', label: 'Election types' },
    { key: 'lifecycleStates', label: 'Lifecycle states' },
    { key: 'positions', label: 'Positions' },
    { key: 'taskStates', label: 'Task states' },
    { key: 'taskPriorities', label: 'Task priorities' },
    { key: 'eventTypes', label: 'Event types' },
    { key: 'movementTypes', label: 'Movement types' }
  ];

  area = { id: 0, parentAreaId: null as number | null, areaTypeId: 0, code: '', nameBn: '', nameEn: '' };
  areaType = { id: 0, code: '', name: '', level: 1 };
  electionType = { id: 0, code: '', name: '' };
  lifecycleState = { id: 0, code: '', name: '', isTerminal: false };
  position = { id: 0, electionTypeId: 0, code: '', name: '' };
  taskState = { id: 0, code: '', name: '', isTerminal: false };
  taskPriority = { id: 0, code: '', name: '', rank: 0 };
  eventType = { id: 0, code: '', name: '' };
  movementType = { id: 0, code: '', name: '', requiresSource: true, requiresDestination: true };

  constructor() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.api.getMasterData().subscribe({
      next: x => {
        this.data.set(x);
        this.syncNextIds();
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Master data could not be loaded.');
        this.loading.set(false);
      }
    });
  }

  selectTab(key: string) {
    this.tab.set(key);
    this.syncNextIds();
  }

  filteredAreas() {
    let list = this.data().areas;
    if (this.areaTypeFilter > 0) {
      list = list.filter(a => a.areaTypeId === this.areaTypeFilter);
    }
    const q = this.areaSearch.trim().toLowerCase();
    if (q) {
      list = list.filter(a =>
        a.code.toLowerCase().includes(q) ||
        (a.nameEn && a.nameEn.toLowerCase().includes(q)) ||
        a.nameBn.toLowerCase().includes(q)
      );
    }
    return list.slice(0, 150);
  }

  nextId(key: string): number {
    const d = this.data();
    switch (key) {
      case 'areas': return (d.areas.length ? Math.max(...d.areas.map(x => x.id)) : 0) + 1;
      case 'areaTypes': return (d.areaTypes.length ? Math.max(...d.areaTypes.map(x => x.id)) : 0) + 1;
      case 'electionTypes': return (d.electionTypes.length ? Math.max(...d.electionTypes.map(x => x.id)) : 0) + 1;
      case 'lifecycleStates': return ((d.lifecycleStates?.length ?? 0) ? Math.max(...(d.lifecycleStates?.map(x => x.id) ?? [0])) : 0) + 1;
      case 'positions': return (d.positions.length ? Math.max(...d.positions.map(x => x.id)) : 0) + 1;
      case 'taskStates': return (d.taskStates.length ? Math.max(...d.taskStates.map(x => x.id)) : 0) + 1;
      case 'taskPriorities': return (d.taskPriorities.length ? Math.max(...d.taskPriorities.map(x => x.id)) : 0) + 1;
      case 'eventTypes': return ((d.eventTypes?.length ?? 0) ? Math.max(...(d.eventTypes?.map(x => x.id) ?? [0])) : 0) + 1;
      case 'movementTypes': return ((d.movementTypes?.length ?? 0) ? Math.max(...(d.movementTypes?.map(x => x.id) ?? [0])) : 0) + 1;
      default: return 1;
    }
  }

  syncNextIds() {
    if (!this.area.id || this.area.id <= 0) this.area.id = this.nextId('areas');
    if (!this.areaType.id || this.areaType.id <= 0) this.areaType.id = this.nextId('areaTypes');
    if (!this.electionType.id || this.electionType.id <= 0) this.electionType.id = this.nextId('electionTypes');
    if (!this.lifecycleState.id || this.lifecycleState.id <= 0) this.lifecycleState.id = this.nextId('lifecycleStates');
    if (!this.position.id || this.position.id <= 0) this.position.id = this.nextId('positions');
    if (!this.taskState.id || this.taskState.id <= 0) this.taskState.id = this.nextId('taskStates');
    if (!this.taskPriority.id || this.taskPriority.id <= 0) this.taskPriority.id = this.nextId('taskPriorities');
    if (!this.eventType.id || this.eventType.id <= 0) this.eventType.id = this.nextId('eventTypes');
    if (!this.movementType.id || this.movementType.id <= 0) this.movementType.id = this.nextId('movementTypes');
  }

  count(key: string) {
    const x = this.data();
    switch (key) {
      case 'areas': return x.areas.length;
      case 'areaTypes': return x.areaTypes.length;
      case 'electionTypes': return x.electionTypes.length;
      case 'lifecycleStates': return x.lifecycleStates?.length ?? 0;
      case 'positions': return x.positions.length;
      case 'taskStates': return x.taskStates.length;
      case 'taskPriorities': return x.taskPriorities.length;
      case 'eventTypes': return x.eventTypes?.length ?? 0;
      case 'movementTypes': return x.movementTypes?.length ?? 0;
      default: return 0;
    }
  }

  tabLabel() { return this.tabs.find(x => x.key === this.tab())?.label ?? 'Reference'; }
  areaTypeName(id: number) { return this.data().areaTypes.find(x => x.id === id)?.name ?? `Type ${id}`; }
  electionTypeName(id: number) { return this.data().electionTypes.find(x => x.id === id)?.name ?? `Type ${id}`; }

  validSimple(x: { code: string; name: string }) { return !!x.code.trim() && !!x.name.trim(); }
  validArea() { return this.area.areaTypeId > 0 && !!this.area.code.trim() && !!this.area.nameBn.trim(); }
  validAreaType() { return this.validSimple(this.areaType) && this.areaType.level > 0; }
  validPosition() { return this.validSimple(this.position) && this.position.electionTypeId > 0; }
  validPriority() { return this.validSimple(this.taskPriority) && this.taskPriority.rank > 0; }
  validMovementType() { return this.validSimple(this.movementType) && (this.movementType.requiresSource || this.movementType.requiresDestination); }

  addArea() {
    this.area.id = this.nextId('areas');
    this.save(this.api.addMasterArea({ ...this.area, nameEn: this.area.nameEn || null }), () => {
      this.area = { id: 0, parentAreaId: null, areaTypeId: 0, code: '', nameBn: '', nameEn: '' };
    });
  }

  addAreaType() {
    this.areaType.id = this.nextId('areaTypes');
    this.save(this.api.addMasterAreaType(this.areaType), () => {
      this.areaType = { id: 0, code: '', name: '', level: 1 };
    });
  }

  addElectionType() {
    this.electionType.id = this.nextId('electionTypes');
    this.save(this.api.addMasterElectionType(this.electionType), () => {
      this.electionType = { id: 0, code: '', name: '' };
    });
  }

  addLifecycleState() {
    this.lifecycleState.id = this.nextId('lifecycleStates');
    this.save(this.api.addMasterLifecycleState(this.lifecycleState), () => {
      this.lifecycleState = { id: 0, code: '', name: '', isTerminal: false };
    });
  }

  addPosition() {
    this.position.id = this.nextId('positions');
    this.save(this.api.addMasterPosition(this.position), () => {
      this.position = { id: 0, electionTypeId: 0, code: '', name: '' };
    });
  }

  addTaskState() {
    this.taskState.id = this.nextId('taskStates');
    this.save(this.api.addMasterTaskState(this.taskState), () => {
      this.taskState = { id: 0, code: '', name: '', isTerminal: false };
    });
  }

  addTaskPriority() {
    this.taskPriority.id = this.nextId('taskPriorities');
    this.save(this.api.addMasterTaskPriority(this.taskPriority), () => {
      this.taskPriority = { id: 0, code: '', name: '', rank: 0 };
    });
  }

  addEventType() {
    this.eventType.id = this.nextId('eventTypes');
    this.save(this.api.addMasterEventType(this.eventType), () => {
      this.eventType = { id: 0, code: '', name: '' };
    });
  }

  addMovementType() {
    this.movementType.id = this.nextId('movementTypes');
    this.save(this.api.addMasterMovementType(this.movementType), () => {
      this.movementType = { id: 0, code: '', name: '', requiresSource: true, requiresDestination: true };
    });
  }

  private save<T>(request: Observable<T>, reset: () => void) {
    if (this.saving()) return;
    this.saving.set(true);
    this.error.set('');
    request.subscribe({
      next: () => {
        reset();
        this.notice.set('Master data entry saved to database.');
        this.saving.set(false);
        this.load();
      },
      error: () => {
        this.error.set('Entry could not be saved. Check code uniqueness and related references.');
        this.saving.set(false);
      }
    });
  }
}
