import * as SQLite from 'expo-sqlite';
import { Transaction, CategoryTotal } from '../types';

let db: SQLite.SQLiteDatabase;

export async function getDatabase(): Promise<SQLite.SQLiteDatabase> {
  if (!db) {
    db = await SQLite.openDatabaseAsync('devwallet.db');
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
        date TEXT NOT NULL
      );
    `);
  }
  return db;
}

export async function getTransactions(): Promise<Transaction[]> {
  // TODO: Récupérer toutes les transactions triées par date décroissante
  return [];
}

export async function addTransaction(
  transaction: Omit<Transaction, 'id'>
): Promise<void> {
  // TODO: Insérer une nouvelle transaction dans la base de données
}

export async function deleteTransaction(id: number): Promise<void> {
  // TODO: Supprimer une transaction par son id
}

export async function getBalance(): Promise<{ income: number; expenses: number }> {
  // TODO: Calculer le total des revenus et des dépenses avec SUM et GROUP BY
  return { income: 0, expenses: 0 };
}

export async function getTotalsByCategory(): Promise<CategoryTotal[]> {
  // TODO: Calculer le total des dépenses par catégorie avec SUM et GROUP BY
  return [];
}
