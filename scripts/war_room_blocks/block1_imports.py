# -*- coding: utf-8 -*-

def get_block1():
    return '''import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule, DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import * as QRCode from 'qrcode';
import { AuthService } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import {
  BoothSummary,
  CandidateBoothAgentSummary,
  CandidateElectionResultsSummary,
  CandidateWarRoomSummary,
  CenterDirectoryItem,
  EcExpenseScheduleReport,
  ElectionSymbolSummary,
  CandidateVoterSummary,
  CreateVoterRequest,
  CandidateIncidentSummary,
  CreateIncidentRequest,
  CandidateCampaignEventItem,
  CreateCampaignEventRequest,
  UpdateCampaignEventPermitRequest,
  SmsGatewayConfigDto,
  UpdateSmsGatewayConfigRequest,
  TestSmsRequest,
  SendVoterBroadcastRequest,
  VoterQueueItem,
  SendVoterBroadcastResponse,
  VoterBulkRowDto,
  VoterBulkPreviewResult,
  VoterBulkImportResult,
  CandidateCenterResultItem,
  Form8DetailResponse
} from '../../core/models/api.models';

export type WarRoomTab = 'overview' | 'agents' | 'voters' | 'campaign' | 'incidents' | 'results' | 'expenses' | 'team';
'''

