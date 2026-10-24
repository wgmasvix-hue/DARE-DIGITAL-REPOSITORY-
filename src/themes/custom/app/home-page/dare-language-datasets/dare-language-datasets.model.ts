/**
 * Typed model for the DARE "African Language Datasets" interface.
 *
 * These interfaces mirror the verified catalogue export produced by the DARE
 * harvester (`darelang.dspace.export_web_datasets`). They contain only fields
 * that are safe to publish: no download tokens, no internal paths, no
 * restricted metadata. The generated data module
 * (`dare-language-datasets.data.ts`) is the single source of truth.
 */

export interface DareLanguageCode {
  /** ISO 639 code, e.g. "sn" */
  code: string;
  /** Human-readable name, e.g. "chiShona" */
  name: string;
}

export interface DareLicence {
  /** SPDX identifier when resolved, otherwise null */
  spdx: string | null;
  /** Human-readable licence name */
  name: string | null;
  /** Canonical licence URL */
  url: string | null;
  /** Whether commercial use is permitted (null when unknown) */
  commercialUse: boolean | null;
  /** Whether attribution is required (null when unknown) */
  requiresAttribution: boolean | null;
  /** Internal licence resolution status, e.g. RESOLVED_NONCOMMERCIAL */
  status: string | null;
}

export interface DareAttribution {
  /** Curating organisation or person, when recorded */
  curator: string | null;
  /** Preferred citation, when recorded */
  citation: string | null;
}

export interface DareProvenance {
  /** Canonical source URL */
  sourceUrl: string | null;
  /** Upstream repository URL */
  repository: string | null;
  /** Pinned source revision (commit/tag) */
  revision: string | null;
  /** Retrieval date (ISO-8601), when recorded */
  retrieved: string | null;
  /** Validation status recorded by the harvester */
  validationStatus: string | null;
  /** Short provenance note */
  notes: string;
}

/**
 * Public publication state. These three values are the only states the UI
 * presents and they are mutually exclusive:
 *  - metadata-only: licence resolved, redistribution not approved.
 *  - approved-for-redistribution: explicitly approved for redistribution.
 *  - awaiting-licence-review: licence unresolved/pending or quarantined.
 */
export type DarePublicationState =
  | 'metadata-only'
  | 'approved-for-redistribution'
  | 'awaiting-licence-review';

export interface DareLanguageDataset {
  /** Stable dataset identifier */
  id: string;
  /** Public title */
  title: string;
  /** NLP task, e.g. named-entity-recognition */
  task: string | null;
  /** Covered languages */
  languages: DareLanguageCode[];
  /** Licence details */
  licence: DareLicence;
  /** Attribution details */
  attribution: DareAttribution;
  /** Provenance and source revision */
  provenance: DareProvenance;
  /** Public publication state (drives the badge and gating) */
  publicationState: DarePublicationState;
  /** Internal lifecycle state, shown only in the details panel */
  lifecycleState: string;
  /**
   * Whether the catalogue currently permits a content download. The UI must
   * never render a download link unless this is true.
   */
  downloadPermitted: boolean;
  /** Repository-relative names of approved, public research reports */
  reportLinks: string[];
}
