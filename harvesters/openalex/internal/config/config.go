package config

import (
	"os"
	"time"
)

// Config represents the harvester configuration
type Config struct {
	OpenAlex OpenAlexConfig `yaml:"openalex"`
	DSpace   DSpaceConfig   `yaml:"dspace"`
	Topics   []string       `yaml:"topics"`
	Output   OutputConfig   `yaml:"output"`
	Features FeaturesConfig `yaml:"features"`
}

// OpenAlexConfig represents OpenAlex API settings
type OpenAlexConfig struct {
	Email            string `yaml:"email"`
	BaseURL          string `yaml:"base_url"`
	PerPage          int    `yaml:"per_page"`
	MaxRequests      int    `yaml:"max_requests"`
	RateLimitDelay   int    `yaml:"rate_limit_delay"`
	RequestTimeout   int    `yaml:"request_timeout"`
	MinPublicationYear int  `yaml:"min_publication_year"`
	MaxPublicationYear int  `yaml:"max_publication_year"`
}

// DSpaceConfig represents DSpace settings
type DSpaceConfig struct {
	URL      string `yaml:"url"`
	Username string `yaml:"username"`
	Password string `yaml:"password"`
	APIKey   string `yaml:"api_key"`
	Enabled  bool   `yaml:"enabled"`
}

// OutputConfig represents output settings
type OutputConfig struct {
	Directory string `yaml:"directory"`
	Format    string `yaml:"format"` // json, csv, dublin_core
	Pretty    bool   `yaml:"pretty"`
}

// FeaturesConfig represents feature flags
type FeaturesConfig struct {
	EnableIncremental    bool `yaml:"enable_incremental"`
	EnableDeduplication  bool `yaml:"enable_deduplication"`
	EnableORCIDMatching  bool `yaml:"enable_orcid_matching"`
	EnableVectorIndexing bool `yaml:"enable_vector_indexing"`
}

// GetDefaults returns a config with sensible defaults
func GetDefaults() *Config {
	return &Config{
		OpenAlex: OpenAlexConfig{
			Email:            "harvester@example.com",
			BaseURL:          "https://api.openalex.org",
			PerPage:          100,
			MaxRequests:      1000,
			RateLimitDelay:   100,
			RequestTimeout:   30,
			MinPublicationYear: 2020,
			MaxPublicationYear: int(time.Now().Year()),
		},
		DSpace: DSpaceConfig{
			URL:     "https://dspace.dare.co.zw/server",
			Enabled: false,
		},
		Output: OutputConfig{
			Directory: "./output",
			Format:    "json",
			Pretty:    true,
		},
		Features: FeaturesConfig{
			EnableIncremental:    true,
			EnableDeduplication:  true,
			EnableORCIDMatching:  true,
			EnableVectorIndexing: false,
		},
		Topics: []string{
			"artificial intelligence",
			"machine learning",
			"deep learning",
			"computer vision",
			"natural language processing",
		},
	}
}

// Validate checks if the configuration is valid
func (c *Config) Validate() error {
	if c.OpenAlex.Email == "" {
		c.OpenAlex.Email = "harvester@example.com"
	}

	if c.OpenAlex.BaseURL == "" {
		c.OpenAlex.BaseURL = "https://api.openalex.org"
	}

	if c.OpenAlex.PerPage == 0 {
		c.OpenAlex.PerPage = 100
	}

	if c.OpenAlex.PerPage > 200 {
		c.OpenAlex.PerPage = 200
	}

	if c.OpenAlex.MaxRequests == 0 {
		c.OpenAlex.MaxRequests = 1000
	}

	if c.OpenAlex.RateLimitDelay == 0 {
		c.OpenAlex.RateLimitDelay = 100
	}

	if c.OpenAlex.RequestTimeout == 0 {
		c.OpenAlex.RequestTimeout = 30
	}

	if c.Output.Directory == "" {
		c.Output.Directory = "./output"
	}

	if c.Output.Format == "" {
		c.Output.Format = "json"
	}

	// Create output directory if it doesn't exist
	if err := os.MkdirAll(c.Output.Directory, 0755); err != nil {
		return err
	}

	return nil
}
