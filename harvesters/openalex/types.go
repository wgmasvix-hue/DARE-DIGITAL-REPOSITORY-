package main

import "time"

// OpenAlex API Response Types
type WorksResponse struct {
	Results []Work `json:"results"`
	Meta    Meta   `json:"meta"`
}

type Work struct {
	ID                    string                 `json:"id"`
	DOI                   string                 `json:"doi"`
	Title                 string                 `json:"title"`
	PublicationDate       string                 `json:"publication_date"`
	PublicationYear       int                    `json:"publication_year"`
	AbstractInvertedIndex map[string][]int       `json:"abstract_inverted_index"`
	Authorships           []Authorship           `json:"authorships"`
	Concepts              []Concept              `json:"concepts"`
	ReferencedWorks       []string               `json:"referenced_works"`
	RelatedWorks          []string               `json:"related_works"`
	URL                   string                 `json:"url"`
	HostVenue             *Venue                 `json:"host_venue"`
	IssueNumber           string                 `json:"issue"`
	VolumeNumber          string                 `json:"volume"`
	Pages                 string                 `json:"pages"`
	OpenAccess            OpenAccess             `json:"open_access"`
	TypeCrossref          string                 `json:"type_crossref"`
	Counts                map[string]interface{} `json:"counts"`
}

type Authorship struct {
	Author        Author  `json:"author"`
	Institutions  []Inst  `json:"institutions"`
	Position      int     `json:"author_position"`
	RawAffiliationStrings []string `json:"raw_affiliation_strings"`
}

type Author struct {
	ID   string `json:"id"`
	Name string `json:"display_name"`
	ORCID string `json:"orcid"`
}

type Inst struct {
	ID          string `json:"id"`
	DisplayName string `json:"display_name"`
	CountryCode string `json:"country_code"`
	Type        string `json:"type"`
}

type Concept struct {
	ID             string  `json:"id"`
	DisplayName    string  `json:"display_name"`
	Level          int     `json:"level"`
	Score          float64 `json:"score"`
	WorksCount     int     `json:"works_count"`
	CitedByCount   int     `json:"cited_by_count"`
}

type Venue struct {
	ID          string `json:"id"`
	DisplayName string `json:"display_name"`
	ISSN        []string `json:"issn_l"`
	PublisherID string `json:"publisher"`
}

type OpenAccess struct {
	IsOA         bool   `json:"is_oa"`
	OAStatus     string `json:"oa_status"`
	OAURL        string `json:"oa_url"`
	License      string `json:"license"`
}

type Meta struct {
	Count   int   `json:"count"`
	DBResponseTime int   `json:"db_response_time_ms"`
	PageNumber int `json:"page"`
	PerPage  int   `json:"per_page"`
}

// Dublin Core Metadata (for DSpace import)
type DublinCoreRecord struct {
	Handle        string
	Title         string
	Creator       []string
	Subject       []string
	Description   string
	Date          string
	Type          string
	Format        string
	Identifier    string
	Language      string
	Publisher     string
	Relation      []string
	Coverage      string
	Rights        string
	Source        string
	Harvested     bool
	HarvestedDate time.Time
}

// Search Topic Configuration
type SearchTopic struct {
	Name       string   `json:"name"`
	Query      string   `json:"query"`
	Filters    Filters  `json:"filters"`
	Enabled    bool     `json:"enabled"`
	LastSync   time.Time `json:"last_sync"`
	RecordCount int     `json:"record_count"`
}

type Filters struct {
	MinPublicationYear int    `json:"min_publication_year,omitempty"`
	MaxPublicationYear int    `json:"max_publication_year,omitempty"`
	HasDOI            bool   `json:"has_doi,omitempty"`
	OpenAccessOnly    bool   `json:"open_access_only,omitempty"`
	CountryCode       string `json:"country_code,omitempty"`
}

// Harvester Configuration
type HarvesterConfig struct {
	BaseURL              string
	PerPage              int
	MaxRequests          int
	RateLimitDelay       int
	DSpaceURL            string
	DSpaceAPIKey         string
	EnableIncremental    bool
	EnableDeduplication  bool
	EnableORCIDMatching  bool
	EnableVectorIndexing bool
	Topics               []SearchTopic
}

// Harvester State
type HarvesterState struct {
	LastHarvested map[string]time.Time `json:"last_harvested"`
	ProcessedDOIs map[string]bool      `json:"processed_dois"`
}

// Import Statistics
type ImportStats struct {
	TotalProcessed      int
	Successfully Imported int
	Duplicates          int
	Errors              int
	Duration            time.Duration
	StartTime           time.Time
	EndTime             time.Time
}
