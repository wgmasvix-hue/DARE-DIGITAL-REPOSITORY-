package config

import (
	"fmt"
	"os"
	"path/filepath"
)

// LoadFromFile loads configuration from a YAML file
func LoadFromFile(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	config := GetDefaults()

	// Parse YAML manually (simple approach without external dependency)
	if err := parseYAML(string(data), config); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	if err := config.Validate(); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	return config, nil
}

// SaveToFile saves configuration to a YAML file
func SaveToFile(config *Config, path string) error {
	// Create directory if it doesn't exist
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return err
	}

	yaml := generateYAML(config)
	if err := os.WriteFile(path, []byte(yaml), 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// parseYAML is a simple YAML parser for our configuration format
func parseYAML(content string, config *Config) error {
	// For now, use a simple line-by-line parser
	// In production, you'd want to use gopkg.in/yaml.v3
	lines := splitLines(content)

	var currentSection string

	for _, line := range lines {
		line = trimComment(line)
		if line == "" {
			continue
		}

		if isSection(line) {
			currentSection = getSection(line)
			continue
		}

		key, value := parseLine(line)
		if key == "" {
			continue
		}

		parseKeyValue(config, currentSection, key, value)
	}

	return nil
}

// generateYAML generates YAML content from config
func generateYAML(config *Config) string {
	return `# OpenAlex Harvester Configuration

openalex:
  email: ` + config.OpenAlex.Email + `
  base_url: ` + config.OpenAlex.BaseURL + `
  per_page: ` + fmt.Sprintf("%d", config.OpenAlex.PerPage) + `
  max_requests: ` + fmt.Sprintf("%d", config.OpenAlex.MaxRequests) + `
  rate_limit_delay: ` + fmt.Sprintf("%d", config.OpenAlex.RateLimitDelay) + `
  request_timeout: ` + fmt.Sprintf("%d", config.OpenAlex.RequestTimeout) + `
  min_publication_year: ` + fmt.Sprintf("%d", config.OpenAlex.MinPublicationYear) + `
  max_publication_year: ` + fmt.Sprintf("%d", config.OpenAlex.MaxPublicationYear) + `

dspace:
  url: ` + config.DSpace.URL + `
  username: ` + config.DSpace.Username + `
  password: ""
  api_key: ""
  enabled: ` + fmt.Sprintf("%v", config.DSpace.Enabled) + `

output:
  directory: ` + config.Output.Directory + `
  format: ` + config.Output.Format + `
  pretty: ` + fmt.Sprintf("%v", config.Output.Pretty) + `

features:
  enable_incremental: ` + fmt.Sprintf("%v", config.Features.EnableIncremental) + `
  enable_deduplication: ` + fmt.Sprintf("%v", config.Features.EnableDeduplication) + `
  enable_orcid_matching: ` + fmt.Sprintf("%v", config.Features.EnableORCIDMatching) + `
  enable_vector_indexing: ` + fmt.Sprintf("%v", config.Features.EnableVectorIndexing) + `

topics:
` + generateTopicsList(config.Topics) + `
`
}

// generateTopicsList generates YAML list of topics
func generateTopicsList(topics []string) string {
	result := ""
	for _, topic := range topics {
		result += "  - " + topic + "\n"
	}
	return result
}

// Helper functions
func splitLines(s string) []string {
	var lines []string
	var current string

	for _, r := range s {
		if r == '\n' {
			lines = append(lines, current)
			current = ""
		} else {
			current += string(r)
		}
	}

	if current != "" {
		lines = append(lines, current)
	}

	return lines
}

func trimComment(line string) string {
	for i, r := range line {
		if r == '#' {
			return line[:i]
		}
	}
	return line
}

func trim(s string) string {
	for len(s) > 0 && (s[0] == ' ' || s[0] == '\t') {
		s = s[1:]
	}
	for len(s) > 0 && (s[len(s)-1] == ' ' || s[len(s)-1] == '\t') {
		s = s[:len(s)-1]
	}
	return s
}

func isSection(line string) bool {
	line = trim(line)
	return len(line) > 0 && line[0] != ' ' && line[len(line)-1] == ':'
}

func getSection(line string) string {
	line = trim(line)
	if len(line) > 0 && line[len(line)-1] == ':' {
		return line[:len(line)-1]
	}
	return ""
}

func parseLine(line string) (string, string) {
	line = trim(line)

	// Skip if starts with space (sub-key)
	if len(line) > 0 && line[0] == ' ' {
		line = trim(line)
	}

	for i, r := range line {
		if r == ':' {
			key := trim(line[:i])
			value := trim(line[i+1:])
			return key, value
		}
	}

	return "", ""
}

func parseKeyValue(config *Config, section, key, value string) {
	switch section {
	case "openalex":
		switch key {
		case "email":
			config.OpenAlex.Email = value
		case "base_url":
			config.OpenAlex.BaseURL = value
		case "per_page":
			config.OpenAlex.PerPage = parseInt(value, 100)
		case "max_requests":
			config.OpenAlex.MaxRequests = parseInt(value, 1000)
		case "rate_limit_delay":
			config.OpenAlex.RateLimitDelay = parseInt(value, 100)
		case "request_timeout":
			config.OpenAlex.RequestTimeout = parseInt(value, 30)
		case "min_publication_year":
			config.OpenAlex.MinPublicationYear = parseInt(value, 2020)
		case "max_publication_year":
			config.OpenAlex.MaxPublicationYear = parseInt(value, 2024)
		}

	case "dspace":
		switch key {
		case "url":
			config.DSpace.URL = value
		case "username":
			config.DSpace.Username = value
		case "password":
			config.DSpace.Password = value
		case "api_key":
			config.DSpace.APIKey = value
		case "enabled":
			config.DSpace.Enabled = parseBool(value)
		}

	case "output":
		switch key {
		case "directory":
			config.Output.Directory = value
		case "format":
			config.Output.Format = value
		case "pretty":
			config.Output.Pretty = parseBool(value)
		}

	case "features":
		switch key {
		case "enable_incremental":
			config.Features.EnableIncremental = parseBool(value)
		case "enable_deduplication":
			config.Features.EnableDeduplication = parseBool(value)
		case "enable_orcid_matching":
			config.Features.EnableORCIDMatching = parseBool(value)
		case "enable_vector_indexing":
			config.Features.EnableVectorIndexing = parseBool(value)
		}

	case "topics":
		if key == "-" {
			config.Topics = append(config.Topics, value)
		}
	}
}

func parseInt(s string, defaultVal int) int {
	for _, r := range s {
		if r < '0' || r > '9' {
			return defaultVal
		}
	}

	result := 0
	for _, r := range s {
		result = result*10 + int(r-'0')
	}

	return result
}

func parseBool(s string) bool {
	s = trim(s)
	switch s {
	case "true", "yes", "1", "on":
		return true
	default:
		return false
	}
}
