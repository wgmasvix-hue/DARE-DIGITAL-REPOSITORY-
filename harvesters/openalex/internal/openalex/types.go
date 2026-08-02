package openalex

import "time"

// WorksResponse represents the OpenAlex API response
type WorksResponse struct {
	Results []Work `json:"results"`
	Meta    Meta   `json:"meta"`
}

// Work represents a scholarly work from OpenAlex
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

// Authorship represents an author of a work
type Authorship struct {
	Author                Author   `json:"author"`
	Institutions          []Inst   `json:"institutions"`
	Position              int      `json:"author_position"`
	RawAffiliationStrings []string `json:"raw_affiliation_strings"`
}

// Author represents a researcher
type Author struct {
	ID    string `json:"id"`
	Name  string `json:"display_name"`
	ORCID string `json:"orcid"`
}

// Inst represents an institution
type Inst struct {
	ID          string `json:"id"`
	DisplayName string `json:"display_name"`
	CountryCode string `json:"country_code"`
	Type        string `json:"type"`
}

// Concept represents a research concept
type Concept struct {
	ID           string  `json:"id"`
	DisplayName  string  `json:"display_name"`
	Level        int     `json:"level"`
	Score        float64 `json:"score"`
	WorksCount   int     `json:"works_count"`
	CitedByCount int     `json:"cited_by_count"`
}

// Venue represents a publication venue
type Venue struct {
	ID          string   `json:"id"`
	DisplayName string   `json:"display_name"`
	ISSN        []string `json:"issn_l"`
	PublisherID string   `json:"publisher"`
}

// OpenAccess represents open access status
type OpenAccess struct {
	IsOA     bool   `json:"is_oa"`
	OAStatus string `json:"oa_status"`
	OAURL    string `json:"oa_url"`
	License  string `json:"license"`
}

// Meta represents metadata about the API response
type Meta struct {
	Count          int `json:"count"`
	DBResponseTime int `json:"db_response_time_ms"`
	PageNumber     int `json:"page"`
	PerPage        int `json:"per_page"`
}

// DublinCoreRecord represents Dublin Core metadata for DSpace
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

// HarvestStats represents harvesting statistics
type HarvestStats struct {
	TotalProcessed       int
	SuccessfullyImported int
	Duplicates           int
	Errors               int
	Duration             time.Duration
	StartTime            time.Time
	EndTime              time.Time
}
