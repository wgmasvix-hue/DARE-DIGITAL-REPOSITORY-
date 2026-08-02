package harvester

import (
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/chengetai/openalex-harvester/internal/config"
	"github.com/chengetai/openalex-harvester/internal/openalex"
	"github.com/chengetai/openalex-harvester/internal/storage"
	"github.com/go-resty/resty/v2"
)

// Harvester manages OpenAlex data harvesting
type Harvester struct {
	config *config.Config
	client *resty.Client
	store  *storage.Store
	stats  *openalex.HarvestStats
}

// New creates a new Harvester instance
func New(cfg *config.Config, store *storage.Store) *Harvester {
	return &Harvester{
		config: cfg,
		client: resty.New(),
		store:  store,
		stats: &openalex.HarvestStats{
			StartTime: time.Now(),
		},
	}
}

// HarvestTopic harvests works for a specific topic
func (h *Harvester) HarvestTopic(topic string, limit int, dryRun bool) error {
	log.Printf("Harvesting topic: %s\n", topic)

	page := 1
	requestCount := 0
	topicLimit := limit

	for {
		if requestCount >= h.config.OpenAlex.MaxRequests {
			log.Printf("Reached max requests limit for topic: %s\n", topic)
			break
		}

		if topicLimit > 0 && h.stats.TotalProcessed >= topicLimit {
			log.Printf("Reached result limit for topic: %s\n", topic)
			break
		}

		works, err := h.fetchWorks(topic, page)
		if err != nil {
			log.Printf("Error fetching works for topic %s (page %d): %v\n", topic, page, err)
			h.stats.Errors++
			continue
		}

		if len(works.Results) == 0 {
			log.Printf("No more results for topic: %s\n", topic)
			break
		}

		for _, work := range works.Results {
			if topicLimit > 0 && h.stats.TotalProcessed >= topicLimit {
				break
			}

			h.stats.TotalProcessed++

			if h.config.Features.EnableDeduplication && h.store.IsDuplicate(work.DOI) {
				h.stats.Duplicates++
				log.Printf("Duplicate found (DOI: %s), skipping\n", work.DOI)
				continue
			}

			dcRecord := h.convertToDublinCore(work)

			if !dryRun {
				if err := h.store.SaveRecord(dcRecord); err != nil {
					h.stats.Errors++
					log.Printf("Error saving work %s: %v\n", work.ID, err)
					continue
				}
			}

			h.stats.SuccessfullyImported++
			log.Printf("Processed work: %s (%s)\n", work.Title[:min(50, len(work.Title))], work.DOI)

			if h.config.Features.EnableDeduplication && work.DOI != "" {
				h.store.MarkAsProcessed(work.DOI)
			}
		}

		time.Sleep(time.Duration(h.config.OpenAlex.RateLimitDelay) * time.Millisecond)

		page++
		requestCount++

		if works.Meta.Count < h.config.OpenAlex.PerPage {
			break
		}
	}

	return nil
}

// HarvestTopics harvests all configured topics
func (h *Harvester) HarvestTopics(topics []string, limit int, dryRun bool) error {
	log.Println("Starting harvest for topics...")

	for _, topic := range topics {
		if err := h.HarvestTopic(topic, limit, dryRun); err != nil {
			log.Printf("Error harvesting topic %s: %v\n", topic, err)
		}
	}

	h.stats.EndTime = time.Now()
	h.stats.Duration = h.stats.EndTime.Sub(h.stats.StartTime)

	h.logStats()

	return nil
}

// fetchWorks fetches works from OpenAlex API
func (h *Harvester) fetchWorks(query string, page int) (*openalex.WorksResponse, error) {
	url := fmt.Sprintf("%s/works?search=%s&per-page=%d&page=%d",
		h.config.OpenAlex.BaseURL, query, h.config.OpenAlex.PerPage, page)

	h.client.SetTimeout(time.Duration(h.config.OpenAlex.RequestTimeout) * time.Second)

	resp, err := h.client.R().
		SetHeader("User-Agent", fmt.Sprintf("DARE-OpenAlex-Harvester/1.0 (%s)", h.config.OpenAlex.Email)).
		SetHeader("Accept", "application/json").
		SetResult(&openalex.WorksResponse{}).
		Get(url)

	if err != nil {
		return nil, err
	}

	if resp.StatusCode() != 200 {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode())
	}

	return resp.Result().(*openalex.WorksResponse), nil
}

// convertToDublinCore converts an OpenAlex work to Dublin Core metadata
func (h *Harvester) convertToDublinCore(work openalex.Work) *openalex.DublinCoreRecord {
	record := &openalex.DublinCoreRecord{
		Title:        work.Title,
		Date:         work.PublicationDate,
		Type:         "Scholarly Work",
		Format:       "application/pdf",
		Identifier:   work.DOI,
		Harvested:    true,
		HarvestedDate: time.Now(),
		Language:     "en",
		Source:       "OpenAlex",
		Rights:       "Creative Commons Attribution License",
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
		if concept.Score > 0.5 {
			subjects = append(subjects, concept.DisplayName)
		}
	}
	record.Subject = subjects

	// Create abstract from inverted index if available
	if len(work.AbstractInvertedIndex) > 0 {
		record.Description = h.reconstructAbstract(work.AbstractInvertedIndex)
	}

	// Add venue information
	if work.HostVenue != nil && work.HostVenue.DisplayName != "" {
		record.Publisher = work.HostVenue.DisplayName
	}

	// Set rights based on open access status
	if work.OpenAccess.IsOA {
		record.Rights = fmt.Sprintf("Open Access (%s)", work.OpenAccess.OAStatus)
	}

	return record
}

// reconstructAbstract reconstructs abstract text from inverted index
func (h *Harvester) reconstructAbstract(invertedIndex map[string][]int) string {
	if len(invertedIndex) == 0 {
		return ""
	}

	maxPos := 0
	for _, positions := range invertedIndex {
		for _, pos := range positions {
			if pos > maxPos {
				maxPos = pos
			}
		}
	}

	words := make([]string, maxPos+1)

	for word, positions := range invertedIndex {
		if len(positions) > 0 {
			words[positions[0]] = word
		}
	}

	var result []string
	for _, word := range words {
		if word != "" {
			result = append(result, word)
		}
	}

	return strings.Join(result, " ")
}

// GetStats returns harvest statistics
func (h *Harvester) GetStats() *openalex.HarvestStats {
	return h.stats
}

// logStats logs harvest statistics
func (h *Harvester) logStats() {
	log.Println("\n=== Harvest Statistics ===")
	log.Printf("Total Processed: %d\n", h.stats.TotalProcessed)
	log.Printf("Successfully Imported: %d\n", h.stats.SuccessfullyImported)
	log.Printf("Duplicates: %d\n", h.stats.Duplicates)
	log.Printf("Errors: %d\n", h.stats.Errors)
	log.Printf("Duration: %v\n", h.stats.Duration)
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
