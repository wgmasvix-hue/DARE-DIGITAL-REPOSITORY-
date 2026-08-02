package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"
	"time"
)

// LoadConfig loads the harvester configuration from a JSON file
func LoadConfig(filePath string) (*HarvesterConfig, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var config HarvesterConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, err
	}

	// Set defaults if not provided
	if config.BaseURL == "" {
		config.BaseURL = "https://api.openalex.org"
	}
	if config.PerPage == 0 {
		config.PerPage = 50
	}
	if config.MaxRequests == 0 {
		config.MaxRequests = 1000
	}
	if config.RateLimitDelay == 0 {
		config.RateLimitDelay = 100 // milliseconds
	}

	return &config, nil
}

// LoadTopics loads search topics from a JSON file
func LoadTopics(filePath string) ([]SearchTopic, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var topics []SearchTopic
	if err := json.Unmarshal(data, &topics); err != nil {
		return nil, err
	}

	return topics, nil
}

// SaveState saves harvester state to a JSON file
func SaveState(filePath string, state *HarvesterState) error {
	data, err := json.MarshalIndent(state, "", "  ")
	if err != nil {
		return err
	}

	if err := ioutil.WriteFile(filePath, data, 0644); err != nil {
		return err
	}

	return nil
}

// LoadState loads harvester state from a JSON file
func LoadState(filePath string) (*HarvesterState, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			return &HarvesterState{
				LastHarvested: make(map[string]time.Time),
				ProcessedDOIs: make(map[string]bool),
			}, nil
		}
		return nil, err
	}

	var state HarvesterState
	if err := json.Unmarshal(data, &state); err != nil {
		return nil, err
	}

	return &state, nil
}

// CreateDefaultConfig creates a default configuration file
func CreateDefaultConfig(filePath string) error {
	config := HarvesterConfig{
		BaseURL:              "https://api.openalex.org",
		PerPage:              50,
		MaxRequests:          1000,
		RateLimitDelay:       100,
		DSpaceURL:            "https://dspace.dare.co.zw",
		EnableIncremental:    true,
		EnableDeduplication:  true,
		EnableORCIDMatching:  true,
		EnableVectorIndexing: true,
		Topics:               make([]SearchTopic, 0),
	}

	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}

	if err := ioutil.WriteFile(filePath, data, 0644); err != nil {
		return err
	}

	log.Printf("Created default configuration at %s\n", filePath)
	return nil
}

// CreateDefaultTopics creates a default topics configuration file
func CreateDefaultTopics(filePath string) error {
	topics := []SearchTopic{
		{
			Name:    "Artificial Intelligence",
			Query:   "artificial intelligence",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Machine Learning",
			Query:   "machine learning",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Large Language Models",
			Query:   "large language models",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2021},
		},
		{
			Name:    "Deep Learning",
			Query:   "deep learning",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Computer Vision",
			Query:   "computer vision",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Natural Language Processing",
			Query:   "natural language processing",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Robotics",
			Query:   "robotics",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Food Science",
			Query:   "food science",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Agriculture",
			Query:   "agriculture",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
		{
			Name:    "Climate Change",
			Query:   "climate change",
			Enabled: true,
			Filters: Filters{MinPublicationYear: 2020},
		},
	}

	data, err := json.MarshalIndent(topics, "", "  ")
	if err != nil {
		return err
	}

	if err := ioutil.WriteFile(filePath, data, 0644); err != nil {
		return err
	}

	log.Printf("Created default topics configuration at %s\n", filePath)
	return nil
}
