import express from 'express';
import cors from 'cors'
import dotenv from 'dotenv';
import { connectDB } from './db.js';
import scanRouter from './routes/scan.js';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors())
app.use(express.json());
app.use('/scan', scanRouter);

app.listen(port, async () => {
  console.log(`Backend listening on port ${port}`);
  await connectDB();
});
