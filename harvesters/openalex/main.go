package main

import (
	"flag"
	"log"
	"os"
	"path/filepath"
)

func main() {
	// Define command-line flags
	configPath := flag.String("config", "config.json", "Path to configuration file")
	topicsPath := flag.String("topics", "topics.json", "Path to topics configuration file")
	statePath := flag.String("state", "state.json", "Path to harvester state file")
	initConfig := flag.Bool("init-config", false, "Initialize default configuration files")
	fullHarvest := flag.Bool("full", false, "Perform full harvest instead of incremental")
	topic := flag.String("topic", "", "Harvest specific topic only")
	testAPI := flag.Bool("test-api", false, "Test OpenAlex API connectivity")

	flag.Parse()

	// Initialize logging
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Handle initialization
	if *initConfig {
		homeDir, err := os.UserHomeDir()
		if err != nil {
			homeDir = "."
		}
		configDir := filepath.Join(homeDir, ".dare", "harvester")
		if err := os.MkdirAll(configDir, 0755); err != nil {
			log.Fatalf("Failed to create config directory: %v\n", err)
		}

		defaultConfig := filepath.Join(configDir, "config.json")
		defaultTopics := filepath.Join(configDir, "topics.json")

		if err := CreateDefaultConfig(defaultConfig); err != nil {
			log.Fatalf("Failed to create default config: %v\n", err)
		}

		if err := CreateDefaultTopics(defaultTopics); err != nil {
			log.Fatalf("Failed to create default topics: %v\n", err)
		}

		log.Printf("Configuration initialized at %s\n", configDir)
		return
	}

	// Handle API test
	if *testAPI {
		if err := testOpenAlexAPI(); err != nil {
			log.Fatalf("API test failed: %v\n", err)
		}
		return
	}

	// Load configuration
	config, err := LoadConfig(*configPath)
	if err != nil {
		log.Printf("Warning: Could not load configuration from %s: %v\n", *configPath, err)
		log.Println("Using default configuration")
		config = &HarvesterConfig{
			BaseURL:              "https://api.openalex.org",
			PerPage:              50,
			MaxRequests:          1000,
			RateLimitDelay:       100,
			DSpaceURL:            "https://dspace.dare.co.zw",
			EnableIncremental:    true,
			EnableDeduplication:  true,
			EnableORCIDMatching:  true,
			EnableVectorIndexing: true,
		}
	}

	// Load topics
	topics, err := LoadTopics(*topicsPath)
	if err != nil {
		log.Printf("Warning: Could not load topics from %s: %v\n", *topicsPath, err)
		log.Println("Using empty topics list")
		topics = []SearchTopic{}
	}

	// Filter by specific topic if requested
	if *topic != "" {
		var filtered []SearchTopic
		for _, t := range topics {
			if t.Name == *topic {
				filtered = append(filtered, t)
				break
			}
		}
		if len(filtered) == 0 {
			log.Fatalf("Topic not found: %s\n", *topic)
		}
		topics = filtered
	}

	if len(topics) == 0 {
		log.Println("No topics configured. Run with -init-config to create default configuration.")
		return
	}

	// Create harvester
	harvester := NewHarvester(config)

	// Load previous state if incremental harvesting is enabled
	if config.EnableIncremental && !*fullHarvest {
		if err := harvester.LoadState(*statePath); err != nil {
			log.Printf("Warning: Could not load previous state: %v\n", err)
		}
	}

	// Perform harvesting
	var err error
	if config.EnableIncremental && !*fullHarvest {
		log.Println("Starting incremental harvest...")
		err = harvester.HarvestIncremental(topics)
	} else {
		log.Println("Starting full harvest...")
		err = harvester.HarvestAllTopics(topics)
	}

	if err != nil {
		log.Fatalf("Harvesting failed: %v\n", err)
	}

	// Save state
	if err := harvester.SaveState(*statePath); err != nil {
		log.Printf("Warning: Could not save state: %v\n", err)
	}

	// Print final statistics
	stats := harvester.GetStats()
	log.Printf("\n=== Final Statistics ===\n")
	log.Printf("Duration: %v\n", stats.Duration)
	log.Printf("Total Processed: %d\n", stats.TotalProcessed)
	log.Printf("Successfully Imported: %d\n", stats.Successfully Imported)
	log.Printf("Duplicates Skipped: %d\n", stats.Duplicates)
	log.Printf("Errors: %d\n", stats.Errors)
}

// testOpenAlexAPI tests connectivity to the OpenAlex API
func testOpenAlexAPI() error {
	log.Println("Testing OpenAlex API connectivity...")

	client := NewHarvester(&HarvesterConfig{
		BaseURL:         "https://api.openalex.org",
		PerPage:         10,
		RateLimitDelay:  100,
	})

	works, err := client.client.R().
		SetHeader("User-Agent", "DARE-OpenAlex-Harvester/1.0").
		SetResult(&WorksResponse{}).
		Get("https://api.openalex.org/works?search=artificial%20intelligence&per-page=10")

	if err != nil {
		return err
	}

	if works.StatusCode() != 200 {
		log.Printf("API returned status code: %d\n", works.StatusCode())
		return nil
	}

	response := works.Result().(*WorksResponse)
	log.Printf("✓ API is accessible\n")
	log.Printf("✓ Found %d results for 'artificial intelligence'\n", len(response.Results))
	if len(response.Results) > 0 {
		firstWork := response.Results[0]
		log.Printf("✓ Sample result:\n")
		log.Printf("  Title: %s\n", firstWork.Title)
		log.Printf("  Year: %d\n", firstWork.PublicationYear)
		log.Printf("  DOI: %s\n", firstWork.DOI)
		log.Printf("  Authors: %d\n", len(firstWork.Authorships))
	}

	return nil
}
