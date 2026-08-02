package storage

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/chengetai/openalex-harvester/internal/openalex"
)

// Store manages data persistence
type Store struct {
	outputDir    string
	format       string
	pretty       bool
	processed    map[string]bool
	records      []*openalex.DublinCoreRecord
	csvWriter    *csv.Writer
	csvFile      *os.File
	jsonFile     *os.File
}

// New creates a new Store instance
func New(outputDir, format string, pretty bool) (*Store, error) {
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return nil, err
	}

	store := &Store{
		outputDir: outputDir,
		format:    format,
		pretty:    pretty,
		processed: make(map[string]bool),
		records:   make([]*openalex.DublinCoreRecord, 0),
	}

	// Initialize format-specific files
	if format == "csv" {
		csvPath := filepath.Join(outputDir, fmt.Sprintf("harvest_%s.csv", time.Now().Format("20060102_150405")))
		file, err := os.Create(csvPath)
		if err != nil {
			return nil, err
		}
		store.csvFile = file
		store.csvWriter = csv.NewWriter(file)

		// Write CSV header
		header := []string{"DOI", "Title", "Authors", "Year", "Journal", "URL", "OpenAccess", "Topics"}
		store.csvWriter.Write(header)
	}

	return store, nil
}

// SaveRecord saves a record to storage
func (s *Store) SaveRecord(record *openalex.DublinCoreRecord) error {
	s.records = append(s.records, record)

	switch s.format {
	case "json":
		return s.saveJSON()
	case "csv":
		return s.saveCSV(record)
	case "dublin_core":
		return s.saveDublinCore(record)
	default:
		return s.saveJSON()
	}
}

// saveJSON saves records to JSON file
func (s *Store) saveJSON() error {
	jsonPath := filepath.Join(s.outputDir, "harvest.json")

	var data []byte
	var err error

	if s.pretty {
		data, err = json.MarshalIndent(s.records, "", "  ")
	} else {
		data, err = json.Marshal(s.records)
	}

	if err != nil {
		return err
	}

	return os.WriteFile(jsonPath, data, 0644)
}

// saveCSV saves a record to CSV file
func (s *Store) saveCSV(record *openalex.DublinCoreRecord) error {
	if s.csvWriter == nil {
		return fmt.Errorf("CSV writer not initialized")
	}

	authors := ""
	if len(record.Creator) > 0 {
		authors = record.Creator[0]
		if len(record.Creator) > 1 {
			authors += ", et al."
		}
	}

	topics := ""
	if len(record.Subject) > 0 {
		for i, topic := range record.Subject {
			if i > 0 {
				topics += "; "
			}
			topics += topic
		}
	}

	row := []string{
		record.Identifier,
		record.Title,
		authors,
		record.Date,
		record.Publisher,
		"",
		record.Rights,
		topics,
	}

	return s.csvWriter.Write(row)
}

// saveDublinCore saves a record in Dublin Core XML format
func (s *Store) saveDublinCore(record *openalex.DublinCoreRecord) error {
	dcPath := filepath.Join(s.outputDir, fmt.Sprintf("dc_%s.xml", sanitizeFilename(record.Identifier)))

	xml := generateDublinCoreXML(record)
	return os.WriteFile(dcPath, []byte(xml), 0644)
}

// IsDuplicate checks if a DOI has been processed
func (s *Store) IsDuplicate(doi string) bool {
	if doi == "" {
		return false
	}
	return s.processed[doi]
}

// MarkAsProcessed marks a DOI as processed
func (s *Store) MarkAsProcessed(doi string) {
	if doi != "" {
		s.processed[doi] = true
	}
}

// Close closes any open files
func (s *Store) Close() error {
	if s.csvWriter != nil {
		s.csvWriter.Flush()
	}

	if s.csvFile != nil {
		return s.csvFile.Close()
	}

	return nil
}

// GetRecords returns all stored records
func (s *Store) GetRecords() []*openalex.DublinCoreRecord {
	return s.records
}

// generateDublinCoreXML generates Dublin Core XML for a record
func generateDublinCoreXML(record *openalex.DublinCoreRecord) string {
	xml := `<?xml version="1.0" encoding="UTF-8"?>
<dc:dublinCore xmlns:dc="http://purl.org/dc/elements/1.1/">
`

	if record.Title != "" {
		xml += fmt.Sprintf("  <dc:title>%s</dc:title>\n", escapeXML(record.Title))
	}

	for _, creator := range record.Creator {
		xml += fmt.Sprintf("  <dc:creator>%s</dc:creator>\n", escapeXML(creator))
	}

	for _, subject := range record.Subject {
		xml += fmt.Sprintf("  <dc:subject>%s</dc:subject>\n", escapeXML(subject))
	}

	if record.Description != "" {
		xml += fmt.Sprintf("  <dc:description>%s</dc:description>\n", escapeXML(record.Description))
	}

	if record.Publisher != "" {
		xml += fmt.Sprintf("  <dc:publisher>%s</dc:publisher>\n", escapeXML(record.Publisher))
	}

	if record.Date != "" {
		xml += fmt.Sprintf("  <dc:date>%s</dc:date>\n", record.Date)
	}

	if record.Type != "" {
		xml += fmt.Sprintf("  <dc:type>%s</dc:type>\n", record.Type)
	}

	if record.Identifier != "" {
		xml += fmt.Sprintf("  <dc:identifier>%s</dc:identifier>\n", record.Identifier)
	}

	if record.Language != "" {
		xml += fmt.Sprintf("  <dc:language>%s</dc:language>\n", record.Language)
	}

	if record.Rights != "" {
		xml += fmt.Sprintf("  <dc:rights>%s</dc:rights>\n", escapeXML(record.Rights))
	}

	if record.Source != "" {
		xml += fmt.Sprintf("  <dc:source>%s</dc:source>\n", record.Source)
	}

	xml += `</dc:dublinCore>`

	return xml
}

// escapeXML escapes special XML characters
func escapeXML(s string) string {
	s = stringReplace(s, "&", "&amp;")
	s = stringReplace(s, "<", "&lt;")
	s = stringReplace(s, ">", "&gt;")
	s = stringReplace(s, "\"", "&quot;")
	s = stringReplace(s, "'", "&apos;")
	return s
}

// sanitizeFilename sanitizes a filename
func sanitizeFilename(s string) string {
	result := ""
	for _, r := range s {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '-' || r == '_' {
			result += string(r)
		}
	}
	return result
}

// stringReplace is a simple string replace function
func stringReplace(s, old, new string) string {
	result := ""
	for {
		idx := findString(s, old)
		if idx == -1 {
			result += s
			break
		}
		result += s[:idx] + new
		s = s[idx+len(old):]
	}
	return result
}

// findString finds the index of a substring
func findString(s, substr string) int {
	if len(substr) > len(s) {
		return -1
	}

	for i := 0; i <= len(s)-len(substr); i++ {
		match := true
		for j := 0; j < len(substr); j++ {
			if s[i+j] != substr[j] {
				match = false
				break
			}
		}
		if match {
			return i
		}
	}

	return -1
}
