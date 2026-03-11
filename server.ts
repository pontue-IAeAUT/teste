import express from 'express';
import { createServer as createViteServer } from 'vite';
import Database from 'better-sqlite3';
import crypto from 'crypto';

const db = new Database('roi.db');

db.exec(`
  CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    area TEXT NOT NULL,
    summary TEXT NOT NULL,
    resultType TEXT NOT NULL,
    previousHours REAL,
    previousHourlyRate REAL,
    currentHours REAL,
    currentHourlyRate REAL,
    profit REAL,
    implementationHours REAL NOT NULL,
    implementationHourlyRate REAL NOT NULL,
    extraCosts REAL NOT NULL,
    returnAmount REAL NOT NULL,
    costAmount REAL NOT NULL,
    roi REAL NOT NULL,
    createdAt INTEGER NOT NULL
  )
`);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  app.get('/api/projects', (req, res) => {
    const projects = db.prepare('SELECT * FROM projects ORDER BY createdAt DESC').all();
    res.json(projects);
  });

  app.post('/api/projects', (req, res) => {
    const project = req.body;
    const id = crypto.randomUUID();
    const createdAt = Date.now();

    const stmt = db.prepare(`
      INSERT INTO projects (
        id, name, area, summary, resultType, previousHours, previousHourlyRate,
        currentHours, currentHourlyRate, profit, implementationHours,
        implementationHourlyRate, extraCosts, returnAmount, costAmount, roi, createdAt
      ) VALUES (
        @id, @name, @area, @summary, @resultType, @previousHours, @previousHourlyRate,
        @currentHours, @currentHourlyRate, @profit, @implementationHours,
        @implementationHourlyRate, @extraCosts, @returnAmount, @costAmount, @roi, @createdAt
      )
    `);

    stmt.run({
      id,
      name: project.name,
      area: project.area,
      summary: project.summary,
      resultType: project.resultType,
      previousHours: project.previousHours || null,
      previousHourlyRate: project.previousHourlyRate || null,
      currentHours: project.currentHours || null,
      currentHourlyRate: project.currentHourlyRate || null,
      profit: project.profit || null,
      implementationHours: project.implementationHours || 0,
      implementationHourlyRate: project.implementationHourlyRate || 0,
      extraCosts: project.extraCosts || 0,
      returnAmount: project.returnAmount || 0,
      costAmount: project.costAmount || 0,
      roi: project.roi || 0,
      createdAt
    });

    res.json({ id, ...project, createdAt });
  });

  app.put('/api/projects/:id', (req, res) => {
    const project = req.body;
    const id = req.params.id;

    const stmt = db.prepare(`
      UPDATE projects SET
        name = @name, area = @area, summary = @summary, resultType = @resultType,
        previousHours = @previousHours, previousHourlyRate = @previousHourlyRate,
        currentHours = @currentHours, currentHourlyRate = @currentHourlyRate,
        profit = @profit, implementationHours = @implementationHours,
        implementationHourlyRate = @implementationHourlyRate, extraCosts = @extraCosts,
        returnAmount = @returnAmount, costAmount = @costAmount, roi = @roi
      WHERE id = @id
    `);

    stmt.run({
      id,
      name: project.name,
      area: project.area,
      summary: project.summary,
      resultType: project.resultType,
      previousHours: project.previousHours || null,
      previousHourlyRate: project.previousHourlyRate || null,
      currentHours: project.currentHours || null,
      currentHourlyRate: project.currentHourlyRate || null,
      profit: project.profit || null,
      implementationHours: project.implementationHours || 0,
      implementationHourlyRate: project.implementationHourlyRate || 0,
      extraCosts: project.extraCosts || 0,
      returnAmount: project.returnAmount || 0,
      costAmount: project.costAmount || 0,
      roi: project.roi || 0
    });

    const updatedProject = db.prepare('SELECT * FROM projects WHERE id = ?').get(id);
    res.json(updatedProject);
  });

  app.delete('/api/projects/:id', (req, res) => {
    db.prepare('DELETE FROM projects WHERE id = ?').run(req.params.id);
    res.json({ success: true });
  });

  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static('dist'));
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
