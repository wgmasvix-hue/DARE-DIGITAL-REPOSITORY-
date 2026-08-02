package dspace

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/chengetai/openalex-harvester/internal/config"
	"github.com/chengetai/openalex-harvester/internal/openalex"
	"github.com/go-resty/resty/v2"
)

// Client represents a DSpace API client for DSpace 9
type Client struct {
	config       *config.DSpaceConfig
	client       *resty.Client
	token        string
	collectionID string
}

// New creates a new DSpace client
func New(cfg *config.DSpaceConfig) *Client {
	return &Client{
		config: cfg,
		client: resty.New(),
	}
}

// MetadataValue represents a single metadata value in DSpace 9
type MetadataValue struct {
	Language string `json:"language"`
	Value    string `json:"value"`
	Authority string `json:"authority,omitempty"`
	Confidence int    `json:"confidence,omitempty"`
	Place    int    `json:"place,omitempty"`
}

// Item represents a DSpace 9 item
type Item struct {
	Metadata map[string][]MetadataValue `json:"metadata"`
}

// WorkspaceItem represents a workspace item in DSpace 9
type WorkspaceItem struct {
	ID       int            `json:"id"`
	Item     Item           `json:"item"`
	Submitter json.RawMessage `json:"submitter"`
	Collection json.RawMessage `json:"collection"`
}

// ItemResponse represents the response from DSpace when creating an item
type ItemResponse struct {
	UUID     string                      `json:"uuid"`
	Handle   string                      `json:"handle"`
	Metadata map[string][]MetadataValue `json:"metadata"`
}

// IsEnabled checks if DSpace integration is enabled
func (c *Client) IsEnabled() bool {
	return c.config.Enabled && c.config.URL != ""
}

// Authenticate authenticates with DSpace using API key or credentials
func (c *Client) Authenticate() error {
	if c.config.APIKey != "" {
		// DSpace 9 supports bearer token authentication
		c.token = c.config.APIKey
		log.Println("✓ Using API key authentication")
		return nil
	}

	if c.config.Username == "" || c.config.Password == "" {
		return fmt.Errorf("DSpace credentials not configured")
	}

	// Authenticate with username/password (DSpace 9)
	url := fmt.Sprintf("%s/api/auth/login", c.config.URL)

	c.client.SetTimeout(10 * time.Second)

	resp, err := c.client.R().
		SetHeader("Content-Type", "application/x-www-form-urlencoded").
		SetFormData(map[string]string{
			"username": c.config.Username,
			"password": c.config.Password,
		}).
		Post(url)

	if err != nil {
		return fmt.Errorf("authentication failed: %w", err)
	}

	if resp.StatusCode() != 200 {
		return fmt.Errorf("authentication returned status %d: %s", resp.StatusCode(), string(resp.Body()))
	}

	// Extract token from response (DSpace 9 returns token in Authorization header)
	c.token = strings.TrimPrefix(string(resp.Header().Get("Authorization")), "Bearer ")
	if c.token == "" {
		// Fallback: try to get token from response body
		var auth map[string]string
		json.Unmarshal(resp.Body(), &auth)
		c.token = auth["token"]
	}

	log.Println("✓ Authenticated with DSpace 9")
	return nil
}

// ImportRecord imports a Dublin Core record to DSpace 9
func (c *Client) ImportRecord(record *openalex.DublinCoreRecord) (string, error) {
	if !c.IsEnabled() {
		return "", fmt.Errorf("DSpace integration is not enabled")
	}

	if c.token == "" {
		if err := c.Authenticate(); err != nil {
			return "", err
		}
	}

	// Create workspace item (item in submission workflow)
	item := c.dublinCoreToItem(record)

	url := fmt.Sprintf("%s/api/submission/workspaceitems", c.config.URL)

	c.client.SetTimeout(30 * time.Second)

	resp, err := c.client.R().
		SetHeader("Authorization", fmt.Sprintf("Bearer %s", c.token)).
		SetHeader("Content-Type", "application/json").
		SetHeader("Accept", "application/json").
		SetBody(item).
		SetResult(&WorkspaceItem{}).
		Post(url)

	if err != nil {
		return "", fmt.Errorf("failed to create workspace item: %w", err)
	}

	if resp.StatusCode() >= 400 {
		return "", fmt.Errorf("DSpace returned status %d: %s", resp.StatusCode(), string(resp.Body()))
	}

	wsItem := resp.Result().(*WorkspaceItem)

	log.Printf("✓ Created workspace item in DSpace (ID: %d)\n", wsItem.ID)

	// Note: In production, you'd want to publish the item or handle workflow
	// For now, it's in submission status

	return fmt.Sprintf("workspace-item-%d", wsItem.ID), nil
}

// dublinCoreToItem converts Dublin Core metadata to DSpace 9 item format
func (c *Client) dublinCoreToItem(record *openalex.DublinCoreRecord) *Item {
	item := &Item{
		Metadata: make(map[string][]MetadataValue),
	}

	// Title
	if record.Title != "" {
		item.Metadata["dc.title"] = []MetadataValue{
			{Language: record.Language, Value: record.Title, Place: 0},
		}
	}

	// Authors/Creators
	for i, creator := range record.Creator {
		item.Metadata["dc.creator"] = append(
			item.Metadata["dc.creator"],
			MetadataValue{Language: record.Language, Value: creator, Place: i},
		)
	}

	// Subject/Keywords
	for i, subject := range record.Subject {
		item.Metadata["dc.subject"] = append(
			item.Metadata["dc.subject"],
			MetadataValue{Language: record.Language, Value: subject, Place: i},
		)
	}

	// Description/Abstract
	if record.Description != "" {
		item.Metadata["dc.description.abstract"] = []MetadataValue{
			{Language: record.Language, Value: record.Description, Place: 0},
		}
	}

	// Date
	if record.Date != "" {
		item.Metadata["dc.date.issued"] = []MetadataValue{
			{Value: record.Date, Place: 0},
		}
	}

	// Publisher
	if record.Publisher != "" {
		item.Metadata["dc.publisher"] = []MetadataValue{
			{Value: record.Publisher, Place: 0},
		}
	}

	// Type
	if record.Type != "" {
		item.Metadata["dc.type"] = []MetadataValue{
			{Value: record.Type, Place: 0},
		}
	}

	// Identifier (DOI)
	if record.Identifier != "" {
		item.Metadata["dc.identifier.uri"] = []MetadataValue{
			{Value: record.Identifier, Place: 0},
		}
	}

	// Language
	if record.Language != "" {
		item.Metadata["dc.language.iso"] = []MetadataValue{
			{Value: record.Language, Place: 0},
		}
	}

	// Rights
	if record.Rights != "" {
		item.Metadata["dc.rights"] = []MetadataValue{
			{Value: record.Rights, Place: 0},
		}
	}

	// Source
	if record.Source != "" {
		item.Metadata["dc.source"] = []MetadataValue{
			{Value: record.Source, Place: 0},
		}
	}

	return item
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
