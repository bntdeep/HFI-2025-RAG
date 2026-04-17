import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { attachDebugWebSocket } from './ws/debugConsole.js';
import { pythonClient } from './python/client.js';
import { errorHandler } from './middleware/errorHandler.js';
import healthRouter from './routes/health.js';
import compareRouter from './routes/compare.js';
import countryRouter from './routes/country.js';
import chatRouter from './routes/chat.js';
import documentsRouter from './routes/documents.js';
import metadataRouter from './routes/metadata.js';

const app = express();

app.use(cors({ origin: process.env.CORS_ORIGIN ?? 'http://localhost:5173' }));
app.use(express.json({ limit: '10mb' }));

app.use('/api/health', healthRouter);
app.use('/api/compare', compareRouter);
app.use('/api/country', countryRouter);
app.use('/api/chat', chatRouter);
app.use('/api/documents', documentsRouter);
app.use('/api', metadataRouter);

app.use(errorHandler);

const server = createServer(app);
attachDebugWebSocket(server);

const PORT = parseInt(process.env.PORT ?? '3001', 10);

pythonClient.health()
  .then(() => console.log('Python REST API connected at', process.env.PYTHON_URL ?? 'http://localhost:8080'))
  .catch(() => console.warn('Warning: Python REST API not reachable at startup — will retry on each request'));

server.listen(PORT, () => console.log(`BFF listening on :${PORT}`));
