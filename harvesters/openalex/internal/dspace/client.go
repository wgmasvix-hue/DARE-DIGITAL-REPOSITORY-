package dspace

import (
	"fmt"
	"log"
	"time"

	"github.com/chengetai/openalex-harvester/internal/config"
	"github.com/chengetai/openalex-harvester/internal/openalex"
	"github.com/go-resty/resty/v2"
)

// Client represents a DSpace API client
type Client struct {
	config *config.DSpaceConfig
	client *resty.Client
}

// New creates a new DSpace client
func New(cfg *config.DSpaceConfig) *Client {
	return &Client{
		config: cfg,
		client: resty.New(),
	}
}

// IsEnabled checks if DSpace integration is enabled
func (c *Client) IsEnabled() bool {
	return c.config.Enabled && c.config.URL != ""
}

// ImportRecord imports a Dublin Core record to DSpace
func (c *Client) ImportRecord(record *openalex.DublinCoreRecord) (string, error) {
	if !c.IsEnabled() {
		return "", fmt.Errorf("DSpace integration is not enabled")
	}

	// In production, this would make actual API calls to DSpace
	// For now, we'll just log the import and return a mock handle

	log.Printf("Importing to DSpace: %s\n", record.Title[:min(50, len(record.Title))])

	// TODO: Implement actual DSpace API integration
	// This would involve:
	// 1. Authenticating with DSpace
	// 2. Creating a collection item
	// 3. Adding Dublin Core metadata
	// 4. Publishing the item

	// Mock handle for demonstration
	handle := fmt.Sprintf("123456789/dspace-%d", time.Now().Unix())

	return handle, nil
}

// GetHealthStatus checks DSpace API health
func (c *Client) GetHealthStatus() error {
	if !c.IsEnabled() {
		return fmt.Errorf("DSpace integration is not enabled")
	}

	url := fmt.Sprintf("%s/api/", c.config.URL)

	c.client.SetTimeout(10 * time.Second)

	resp, err := c.client.R().
		SetHeader("Accept", "application/json").
		Get(url)

	if err != nil {
		return fmt.Errorf("failed to connect to DSpace: %w", err)
	}

	if resp.StatusCode() != 200 {
		return fmt.Errorf("DSpace API returned status %d", resp.StatusCode())
	}

	return nil
}

// TestConnection tests the connection to DSpace
func (c *Client) TestConnection() error {
	if !c.IsEnabled() {
		return fmt.Errorf("DSpace integration is not enabled")
	}

	log.Println("Testing DSpace connection...")

	if err := c.GetHealthStatus(); err != nil {
		return err
	}

	log.Println("✓ DSpace connection successful")
	return nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
