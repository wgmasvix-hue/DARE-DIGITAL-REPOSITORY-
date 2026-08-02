package main

import (
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
)

// Harvester manages OpenAlex data harvesting
type Harvester struct {
	config *HarvesterConfig
	client *resty.Client
	state  *HarvesterState
	stats  *ImportStats
}

// NewHarvester creates a new Harvester instance
func NewHarvester(config *HarvesterConfig) *Harvester {
	return &Harvester{
		config: config,
		client: resty.New(),
		state: &HarvesterState{
			LastHarvested: make(map[string]time.Time),
			ProcessedDOIs: make(map[string]bool),
		},
		stats: &ImportStats{
			StartTime: time.Now(),
		},
	}
}

// HarvestTopic harvests works for a specific search topic
func (h *Harvester) HarvestTopic(topic SearchTopic) error {
	log.Printf("Starting harvest for topic: %s\n", topic.Name)

	page := 1
	requestCount := 0

	for {
		if requestCount >= h.config.MaxRequests {
			log.Printf("Reached max requests limit for topic %s\n", topic.Name)
			break
		}

		works, err := h.fetchWorks(topic.Query, page)
		if err != nil {
			log.Printf("Error fetching works for topic %s (page %d): %v\n", topic.Name, page, err)
			return err
		}

		if len(works.Results) == 0 {
			log.Printf("No more results for topic %s\n", topic.Name)
			break
		}

		for _, work := range works.Results {
			if h.shouldProcessWork(work, topic.Filters) {
				dcRecord := h.convertToDublinCore(work)
				h.stats.TotalProcessed++

				if h.config.EnableDeduplication && h.isDuplicate(work.DOI) {
					h.stats.Duplicates++
					log.Printf("Duplicate found (DOI: %s), skipping\n", work.DOI)
					continue
				}

				if h.config.EnableDeduplication && work.DOI != "" {
					h.state.ProcessedDOIs[work.DOI] = true
				}

				if err := h.importToDSpace(dcRecord); err != nil {
					h.stats.Errors++
					log.Printf("Error importing work %s: %v\n", work.ID, err)
					continue
				}

				h.stats.SuccessfullyImported++
				log.Printf("Successfully imported work: %s (%s)\n", work.Title, work.DOI)
			}
		}

		time.Sleep(time.Duration(h.config.RateLimitDelay) * time.Millisecond)

		page++
		requestCount++

		if works.Meta.Count < h.config.PerPage {
			break
		}
	}

	h.state.LastHarvested[topic.Name] = time.Now()
	log.Printf("Completed harvest for topic: %s\n", topic.Name)

	return nil
}

// HarvestAllTopics harvests works for all enabled topics
func (h *Harvester) HarvestAllTopics(topics []SearchTopic) error {
	log.Println("Starting comprehensive harvest for all topics...")

	for _, topic := range topics {
		if !topic.Enabled {
			log.Printf("Skipping disabled topic: %s\n", topic.Name)
			continue
		}

		if err := h.HarvestTopic(topic); err != nil {
			log.Printf("Error harvesting topic %s: %v\n", topic.Name, err)
		}
	}

	h.stats.EndTime = time.Now()
	h.stats.Duration = h.stats.EndTime.Sub(h.stats.StartTime)

	log.Println("\n=== Harvest Statistics ===")
	log.Printf("Total Processed: %d\n", h.stats.TotalProcessed)
	log.Printf("SuccessfullyImported: %d\n", h.stats.SuccessfullyImported)
	log.Printf("Duplicates: %d\n", h.stats.Duplicates)
	log.Printf("Errors: %d\n", h.stats.Errors)
	log.Printf("Duration: %v\n", h.stats.Duration)

	return nil
}

// HarvestIncremental performs incremental harvesting since last sync
func (h *Harvester) HarvestIncremental(topics []SearchTopic) error {
	log.Println("Starting incremental harvest...")

	for _, topic := range topics {
		if !topic.Enabled {
			continue
		}

		lastSync, exists := h.state.LastHarvested[topic.Name]
		if !exists {
			log.Printf("No previous harvest for %s, performing full harvest\n", topic.Name)
			if err := h.HarvestTopic(topic); err != nil {
				return err
			}
		} else {
			// Build query with publication date filter
			daysSinceLast := time.Since(lastSync).Hours() / 24
			log.Printf("Last harvest for %s was %.1f days ago\n", topic.Name, daysSinceLast)

			// For now, perform full harvest. In production, you'd add publication_date filters
			if err := h.HarvestTopic(topic); err != nil {
				return err
			}
		}
	}

	h.stats.EndTime = time.Now()
	h.stats.Duration = h.stats.EndTime.Sub(h.stats.StartTime)

	return nil
}

// fetchWorks fetches works from OpenAlex API
func (h *Harvester) fetchWorks(query string, page int) (*WorksResponse, error) {
	url := fmt.Sprintf("%s/works?search=%s&per-page=%d&page=%d",
		h.config.BaseURL, query, h.config.PerPage, page)

	resp, err := h.client.R().
		SetHeader("User-Agent", "DARE-OpenAlex-Harvester/1.0").
		SetResult(&WorksResponse{}).
		Get(url)

	if err != nil {
		return nil, err
	}

	if resp.StatusCode() != 200 {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode())
	}

	return resp.Result().(*WorksResponse), nil
}

// shouldProcessWork determines if a work should be processed based on filters
func (h *Harvester) shouldProcessWork(work Work, filters Filters) bool {
	if filters.MinPublicationYear > 0 && work.PublicationYear < filters.MinPublicationYear {
		return false
	}

	if filters.MaxPublicationYear > 0 && work.PublicationYear > filters.MaxPublicationYear {
		return false
	}

	if filters.HasDOI && work.DOI == "" {
		return false
	}

	if filters.OpenAccessOnly && !work.OpenAccess.IsOA {
		return false
	}

	return true
}

// isDuplicate checks if a work has already been processed
func (h *Harvester) isDuplicate(doi string) bool {
	if doi == "" {
		return false
	}
	return h.state.ProcessedDOIs[doi]
}

// convertToDublinCore converts an OpenAlex work to Dublin Core metadata
func (h *Harvester) convertToDublinCore(work Work) *DublinCoreRecord {
	record := &DublinCoreRecord{
		Title:       work.Title,
		Date:        work.PublicationDate,
		Type:        "Scholarly Work",
		Format:      "application/pdf",
		Identifier:  work.DOI,
		Harvested:   true,
		HarvestedDate: time.Now(),
	}

	// Extract creators from authorships
	creators := []string{}
	for _, authorship := range work.Authorships {
		if authorship.Author.Name != "" {
			creators = append(creators, authorship.Author.Name)
		}
	}
	record.Creator = creators

	// Extract concepts as subjects
	subjects := []string{}
	for _, concept := range work.Concepts {
		if concept.Score > 0.5 { // Only include high-confidence concepts
			subjects = append(subjects, concept.DisplayName)
		}
	}
	record.Subject = subjects

	// Create abstract from inverted index if available
	if len(work.AbstractInvertedIndex) > 0 {
		record.Description = h.reconstructAbstract(work.AbstractInvertedIndex)
	}

	// Add venue information as publisher
	if work.HostVenue != nil && work.HostVenue.DisplayName != "" {
		record.Publisher = work.HostVenue.DisplayName
	}

	// Set language (default to English)
	record.Language = "en"

	// Set rights
	record.Rights = "Creative Commons Attribution License"
	if work.OpenAccess.IsOA {
		record.Rights = fmt.Sprintf("Open Access (%s)", work.OpenAccess.OAStatus)
	}

	// Set source
	record.Source = "OpenAlex"

	return record
}

// reconstructAbstract reconstructs abstract text from inverted index
func (h *Harvester) reconstructAbstract(invertedIndex map[string][]int) string {
	if len(invertedIndex) == 0 {
		return ""
	}

	// Find the maximum word position
	maxPos := 0
	for _, positions := range invertedIndex {
		for _, pos := range positions {
			if pos > maxPos {
				maxPos = pos
			}
		}
	}

	// Create array to hold words in order
	words := make([]string, maxPos+1)

	// Fill array with words in correct positions
	for word, positions := range invertedIndex {
		if len(positions) > 0 {
			words[positions[0]] = word
		}
	}

	// Join non-empty words
	var result []string
	for _, word := range words {
		if word != "" {
			result = append(result, word)
		}
	}

	return strings.Join(result, " ")
}

// importToDSpace imports a Dublin Core record to DSpace
func (h *Harvester) importToDSpace(record *DublinCoreRecord) error {
	if h.config.DSpaceURL == "" {
		log.Println("DSpace URL not configured, skipping import")
		return nil
	}

	// In production, this would make actual API calls to DSpace
	// For now, we'll just log the import
	log.Printf("Importing to DSpace: %s\n", record.Identifier)

	// TODO: Implement actual DSpace API integration
	// This would involve:
	// 1. Creating a collection item
	// 2. Adding Dublin Core metadata
	// 3. Uploading associated files if available
	// 4. Publishing the item

	return nil
}

// GetStats returns the current harvest statistics
func (h *Harvester) GetStats() *ImportStats {
	return h.stats
}

// GetState returns the current harvester state
func (h *Harvester) GetState() *HarvesterState {
	return h.state
}

// LoadState loads previously saved harvester state
func (h *Harvester) LoadState(filePath string) error {
	state, err := LoadState(filePath)
	if err != nil {
		return err
	}
	h.state = state
	return nil
}

// SaveState saves the current harvester state
func (h *Harvester) SaveState(filePath string) error {
	return SaveState(filePath, h.state)
}
