/**
 * Ghost API Response Types
 *
 * TypeScript interfaces for Ghost API responses and data structures.
 * Based on research in contracts/ documentation.
 */

// TODO: Phase 1 - Define Ghost API response types
// Based on contracts/api-endpoints.md and contracts/content-formats.md

export interface GhostPost {
  id: string;
  title: string;
  slug: string;
  html?: string;
  lexical?: string;
  mobiledoc?: string;
  feature_image?: string;
  featured: boolean;
  status: 'draft' | 'published' | 'scheduled';
  visibility: 'public' | 'members' | 'paid';
  created_at: string;
  updated_at: string;
  published_at?: string;
  custom_excerpt?: string;
  codeinjection_head?: string;
  codeinjection_foot?: string;
  og_image?: string;
  og_title?: string;
  og_description?: string;
  twitter_image?: string;
  twitter_title?: string;
  twitter_description?: string;
  meta_title?: string;
  meta_description?: string;
  email_subject?: string;
  url: string;
  excerpt: string;
  reading_time: number;
  page: boolean;
}

export interface GhostPage extends Omit<GhostPost, 'page'> {
  page: true;
}

export interface GhostTag {
  id: string;
  name: string;
  slug: string;
  description?: string;
  feature_image?: string;
  visibility: 'public' | 'internal';
  og_image?: string;
  og_title?: string;
  og_description?: string;
  twitter_image?: string;
  twitter_title?: string;
  twitter_description?: string;
  meta_title?: string;
  meta_description?: string;
  codeinjection_head?: string;
  codeinjection_foot?: string;
  canonical_url?: string;
  accent_color?: string;
  url: string;
  count: {
    posts: number;
  };
}

export interface GhostAuthor {
  id: string;
  name: string;
  slug: string;
  email?: string;
  profile_image?: string;
  cover_image?: string;
  bio?: string;
  website?: string;
  location?: string;
  facebook?: string;
  twitter?: string;
  meta_title?: string;
  meta_description?: string;
  url: string;
  count: {
    posts: number;
  };
}

export interface GhostMember {
  id: string;
  uuid: string;
  email: string;
  name?: string;
  note?: string;
  subscribed: boolean;
  created_at: string;
  updated_at: string;
  labels: GhostLabel[];
  subscriptions: GhostSubscription[];
  avatar_image?: string;
  comped: boolean;
  email_count: number;
  email_opened_count: number;
  email_open_rate?: number;
}

export interface GhostLabel {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export interface GhostSubscription {
  id: string;
  member_id: string;
  tier_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface GhostTier {
  id: string;
  name: string;
  slug: string;
  description?: string;
  active: boolean;
  type: 'free' | 'paid';
  welcome_page_url?: string;
  created_at: string;
  updated_at: string;
  visibility: 'public' | 'none';
  trial_days: number;
  currency?: string;
  monthly_price?: number;
  yearly_price?: number;
  benefits: string[];
}

export interface GhostSettings {
  title: string;
  description: string;
  logo?: string;
  icon?: string;
  accent_color?: string;
  cover_image?: string;
  facebook?: string;
  twitter?: string;
  lang: string;
  timezone: string;
  codeinjection_head?: string;
  codeinjection_foot?: string;
  navigation: GhostNavigation[];
  secondary_navigation: GhostNavigation[];
  meta_title?: string;
  meta_description?: string;
  og_image?: string;
  og_title?: string;
  og_description?: string;
  twitter_image?: string;
  twitter_title?: string;
  twitter_description?: string;
  url: string;
}

export interface GhostNavigation {
  label: string;
  url: string;
}

export interface GhostWebhook {
  id: string;
  event: string;
  target_url: string;
  name?: string;
  secret?: string;
  api_version: string;
  integration_id: string;
  status: 'available' | 'error';
  last_triggered_at?: string;
  last_triggered_status?: string;
  last_triggered_error?: string;
  created_at: string;
  updated_at: string;
}

// API Response wrappers
export interface GhostApiResponse<T> {
  [key: string]: T[];
  meta?: {
    pagination?: {
      page: number;
      limit: number;
      pages: number;
      total: number;
      next?: number;
      prev?: number;
    };
  };
}

export interface GhostApiSingleResponse<T> {
  [key: string]: T[];
}

// Error types
export interface GhostApiError {
  message: string;
  context?: string;
  type: string;
  details?: string;
  property?: string;
  help?: string;
  code?: string;
  id: string;
}

export interface GhostApiErrorResponse {
  errors: GhostApiError[];
}