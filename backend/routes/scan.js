import express from 'express';
import { getDB } from '../db.js';
import { normalizeString, normalizeVersion } from '../utils/normalize.js';

const router = express.Router();

router.post('/', async (req, res) => {
  try {
    const { applications } = req.body;

    if (!Array.isArray(applications)) {
      return res.status(400).json({ error: 'Missing or invalid "applications" array' });
    }

    const db = getDB();
    const collection = db.collection('vulnerabilities');
    const results = [];

    for (const app of applications) {
      const vendor = normalizeString(app.vendor);
      const product = normalizeString(app.name);
      const version = normalizeVersion(app.version);

      const cves = await collection.find({ vendor, product, version })
        .project({
          _id: 1,
          description: 1,
          severity: 1,
          baseScore: 1,
          cvssVersion: 1,
          published: 1
        })
        .toArray();

      if (cves.length > 0) {
        results.push({
          app: {
            name: app.name,
            vendor: app.vendor,
            version: app.version,
            install_path: app.install_path || ''
          },
          vulnerabilities: cves.map(cve => ({
            cveId: cve._id,
            description: cve.description,
            severity: cve.severity,
            baseScore: cve.baseScore,
            cvssVersion: cve.cvssVersion,
            published: cve.published
          }))
        });
      }
    }

    res.json({ vulnerable_apps: results });
  } catch (err) {
    console.error('Error in /scan:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
