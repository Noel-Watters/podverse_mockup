const express = require('express');
const app = express();
const port = 3001;

// Middleware
app.use(express.json());

// Health check endpoint with basic error handling
app.get('/health', (req, res) => {
  try {
    res.json({ status: 'ok', service: 'podverse-parse-service' });
  } catch (err) {
    res.status(500).json({ status: 'error', message: 'Health check failed' });
  }
});

// placeholder to replace with Jenkins job trigger
function triggerRealParser(url, podcast_index_id) {
  // e.g., axios.post to Jenkins or SQS
  console.log("Trigger real parser here for:", { url, podcast_index_id });
}

// Parse trigger endpoint
app.post("/trigger-parse", async (req, res) => {
  const { url, podcast_index_id } = req.body;

  if (!url || typeof url !== 'string') {
    return res.status(400).json({ success: false, message: "URL is required and must be a string" });
  }

  // podcast_index_id is optional
  if (podcast_index_id !== undefined && typeof podcast_index_id !== 'number') {
    return res.status(400).json({ success: false, message: "podcast_index_id must be a number if provided" });
  }

  triggerRealParser(url, podcast_index_id);

  console.log("Would trigger parser for:", url, podcast_index_id);
  res.json({ success: true, message: "Simulated parser trigger" });
});

// Basic graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Start server
app.listen(port, () => {
  console.log(`Parse service listening on port ${port}`);
});
  