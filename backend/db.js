import { MongoClient } from 'mongodb';
import dotenv from 'dotenv';

dotenv.config();

let db = null;

export async function connectDB() {
  if (db) return db;

  const uri = process.env.MONGO_URI;

  const client = new MongoClient(uri);
  await client.connect();
  db = client.db();
  console.log('Connected to MongoDB');
  return db;
}

export function getDB() {
  if (!db) throw new Error('DB not connected');
  return db;
}
