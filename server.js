const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { connectDB, disconnectDB } = require('./config/db');
const { errorHandler, notFound } = require('./middleware/errorMiddleware');
const { apiLimiter } = require('./middleware/rateLimiter');

// Route handlers
const healthRoutes = require('./routes/healthRoutes');
const authRoutes = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const assessmentRoutes = require('./routes/assessmentRoutes');
const skillRoutes = require('./routes/skillRoutes');
const resumeRoutes = require('./routes/resumeRoutes');
const analysisRoutes = require('./routes/analysisRoutes');
const roadmapRoutes = require('./routes/roadmapRoutes');
const progressRoutes = require('./routes/progressRoutes');

const app = express();

// Security Headers
app.use(helmet());

// CORS configuration for allowed frontend origins
const rawFrontendUrls = process.env.FRONTEND_URL || 'http://localhost:5173,http://127.0.0.1:5173';
const allowedOrigins = rawFrontendUrls.split(',').map((url) => url.trim().replace(/\/$/, ''));

app.use(
  cors({
    origin: (origin, callback) => {
      // Allow requests with no origin (like mobile apps, curl, server-to-server, or test runner)
      if (!origin) return callback(null, true);
      if (allowedOrigins.indexOf(origin) !== -1 || process.env.NODE_ENV === 'development') {
        return callback(null, true);
      }
      return callback(new Error(`CORS policy blocked access from origin: ${origin}`));
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  })
);

// Request Parsing
app.use(express.json({ limit: '2mb' }));
app.use(express.urlencoded({ extended: true, limit: '2mb' }));

// General rate limiter on API endpoints
app.use('/api', apiLimiter);

// Mount API routes
app.use('/api/health', healthRoutes);
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/assessments', assessmentRoutes);
app.use('/api/skills', skillRoutes);
app.use('/api/resumes', resumeRoutes);
app.use('/api/analyses', analysisRoutes);
app.use('/api/roadmaps', roadmapRoutes);
app.use('/api/progress', progressRoutes);

// Root route friendly welcome message
app.get('/', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'SkillSyncAI REST API Backend is operational. Access endpoints via /api.',
    docs: '/api/health',
  });
});

// 404 & Centralized Error Handlers
app.use(notFound);
app.use(errorHandler);

const PORT = process.env.PORT || 5000;
let server = null;

// Start server if not running in test runner
if (process.env.NODE_ENV !== 'test') {
  (async () => {
    try {
      await connectDB();
    } catch (dbErr) {
      console.warn('[Server Warning] Continuing to start server in degraded mode while database is offline.');
    }

    server = app.listen(PORT, () => {
      console.log(`[SkillSyncAI Backend] Running in ${process.env.NODE_ENV || 'development'} mode on port ${PORT}`);
      console.log(`[SkillSyncAI Backend] Health Check available at http://localhost:${PORT}/api/health`);
    });

    const shutdown = async (signal) => {
      console.log(`\n[SkillSyncAI Backend] Received ${signal}. Commencing graceful shutdown...`);
      if (server) {
        server.close(async () => {
          await disconnectDB();
          console.log('[SkillSyncAI Backend] Process terminated gracefully.');
          process.exit(0);
        });
      }
    };

    process.on('SIGINT', () => shutdown('SIGINT'));
    process.on('SIGTERM', () => shutdown('SIGTERM'));
  })();
}

module.exports = app;
