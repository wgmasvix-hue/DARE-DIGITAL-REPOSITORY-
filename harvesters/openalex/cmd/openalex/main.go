package main

import (
	"flag"
	"log"

	"github.com/chengetai/openalex-harvester/internal/config"
	"github.com/chengetai/openalex-harvester/internal/dspace"
	"github.com/chengetai/openalex-harvester/internal/harvester"
	"github.com/chengetai/openalex-harvester/internal/storage"
)

func main() {
	// Define command-line flags
	configPath := flag.String("config", "configs/config.yaml", "Path to configuration file")
	initConfig := flag.Bool("init-config", false, "Initialize default configuration")
	testAPI := flag.Bool("test-api", false, "Test OpenAlex API connectivity")
	testDSpace := flag.Bool("test-dspace", false, "Test DSpace connection")

	// Harvest options
	topic := flag.String("topic", "", "Harvest specific topic only")
	limit := flag.Int("limit", 0, "Limit results for testing (0 = no limit)")

	// Export options
	exportJSON := flag.Bool("export-json", false, "Export results as JSON only")
	exportCSV := flag.Bool("export-csv", false, "Export results as CSV")
	exportDublinCore := flag.Bool("export-dc", false, "Export results in Dublin Core format")

	// Import options
	importDSpace := flag.Bool("import-dspace", false, "Import directly into DSpace")
	dryRun := flag.Bool("dry-run", false, "Run without actually saving/importing")

	flag.Parse()

	// Initialize logging
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Handle initialization
	if *initConfig {
		handleInitConfig(*configPath)
		return
	}

	// Load configuration
	cfg, err := config.LoadFromFile(*configPath)
	if err != nil {
		log.Printf("Warning: Could not load configuration from %s: %v\n", *configPath, err)
		log.Println("Using default configuration")
		cfg = config.GetDefaults()
	}

	log.Printf("Configuration loaded from: %s\n", *configPath)

	// Handle API test
	if *testAPI {
		handleTestAPI(cfg)
		return
	}

	// Handle DSpace test
	if *testDSpace {
		handleTestDSpace(cfg)
		return
	}

	// Determine topics to harvest
	topics := cfg.Topics
	if *topic != "" {
		topics = []string{*topic}
	}

	if len(topics) == 0 {
		log.Fatalln("No topics configured. Run with -init-config to create default configuration.")
	}

	// Determine export format
	format := "json"
	if *exportCSV {
		format = "csv"
	} else if *exportDublinCore {
		format = "dublin_core"
	}

	if *importDSpace && *exportJSON {
		log.Fatalln("Cannot use both -import-dspace and -export-json")
	}

	// Create storage
	store, err := storage.New(cfg.Output.Directory, format, cfg.Output.Pretty)
	if err != nil {
		log.Fatalf("Failed to create storage: %v\n", err)
	}
	defer store.Close()

	// Create harvester
	h := harvester.New(cfg, store)

	// Perform harvesting
	log.Printf("Starting harvest for topics: %v\n", topics)
	if *limit > 0 {
		log.Printf("Result limit: %d records per topic\n", *limit)
	}
	if *dryRun {
		log.Println("DRY RUN mode enabled - no data will be saved/imported")
	}

	if err := h.HarvestTopics(topics, *limit, *dryRun); err != nil {
		log.Fatalf("Harvesting failed: %v\n", err)
	}

	// Import to DSpace if requested
	if *importDSpace && !*dryRun {
		handleDSpaceImport(cfg, store)
	}

	// Print statistics
	stats := h.GetStats()
	log.Printf("\nOutput saved to: %s\n", cfg.Output.Directory)
	log.Printf("Total records: %d\n", len(store.GetRecords()))
	log.Printf("Successfully processed: %d\n", stats.SuccessfullyImported)
}

// handleInitConfig initializes default configuration
func handleInitConfig(configPath string) {
	cfg := config.GetDefaults()

	if err := config.SaveToFile(cfg, configPath); err != nil {
		log.Fatalf("Failed to create configuration: %v\n", err)
	}

	log.Printf("✓ Configuration initialized at: %s\n", configPath)
	log.Println("\nEdit the configuration file to set your OpenAlex email and DSpace URL")
}

// handleTestAPI tests OpenAlex API connectivity
func handleTestAPI(cfg *config.Config) {
	log.Println("Testing OpenAlex API connectivity...")
	log.Printf("API URL: %s\n", cfg.OpenAlex.BaseURL)
	log.Printf("Email: %s\n", cfg.OpenAlex.Email)

	// Create a temporary harvester to test connectivity
	store, err := storage.New(cfg.Output.Directory, "json", false)
	if err != nil {
		log.Fatalf("Failed to create storage: %v\n", err)
	}
	defer store.Close()

	h := harvester.New(cfg, store)

	// Try to fetch one result
	if err := h.HarvestTopic("test", 1, true); err != nil {
		log.Fatalf("✗ API test failed: %v\n", err)
	}

	log.Println("✓ API is accessible and responsive")
}

// handleTestDSpace tests DSpace connection
func handleTestDSpace(cfg *config.Config) {
	log.Println("Testing DSpace connection...")

	client := dspace.New(&cfg.DSpace)

	if err := client.TestConnection(); err != nil {
		log.Fatalf("✗ DSpace connection failed: %v\n", err)
	}

	log.Println("✓ DSpace connection successful")
}

// handleDSpaceImport imports records to DSpace
func handleDSpaceImport(cfg *config.Config, store *storage.Store) {
	log.Println("\nImporting records to DSpace...")

	client := dspace.New(&cfg.DSpace)

	if !client.IsEnabled() {
		log.Println("Warning: DSpace integration is not enabled in configuration")
		return
	}

	records := store.GetRecords()
	successCount := 0
	errorCount := 0

	for i, record := range records {
		handle, err := client.ImportRecord(record)
		if err != nil {
			log.Printf("[%d/%d] Error importing %s: %v\n", i+1, len(records), record.Title, err)
			errorCount++
			continue
		}

		log.Printf("[%d/%d] Imported successfully (Handle: %s)\n", i+1, len(records), handle)
		successCount++
	}

	log.Printf("\n✓ Import complete: %d successful, %d errors\n", successCount, errorCount)
}
