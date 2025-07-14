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

// Parse trigger endpoint
app.post("/trigger-parse", async (req, res) => {
  const { url, podcast_index_id } = req.body;
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
  