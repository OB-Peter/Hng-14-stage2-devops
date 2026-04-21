const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

// BUG 11 FIX: Read API URL from environment variable
const API_URL = process.env.API_URL || "http://api:8000";
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'views')));

// BUG 13 FIX: Add health endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// BUG 14 FIX: Pass payload through to API
app.post('/submit', async (req, res) => {
  try {
    const payload = req.body.payload || "";
    const response = await axios.post(`${API_URL}/jobs`, { payload });
    res.json(response.data);
  } catch (err) {
    const status = err.response?.status || 500;
    res.status(status).json({ error: "Failed to submit job" });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    const status = err.response?.status || 500;
    res.status(status).json({ error: "Failed to get job status" });
  }
});

const server = app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
  console.log(`API URL: ${API_URL}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  server.close(() => process.exit(0));
});