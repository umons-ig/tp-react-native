import { useState, useCallback } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from 'expo-router';
import { CategoryTotal } from '../../types';
import { getBalance, getTotalsByCategory } from '../../lib/database';

export default function StatsScreen() {
  const [income, setIncome] = useState(0);
  const [expenses, setExpenses] = useState(0);
  const [categoryTotals, setCategoryTotals] = useState<CategoryTotal[]>([]);
  const [loading, setLoading] = useState(true);

  useFocusEffect(
    useCallback(() => {
      loadStats();
    }, [])
  );

  async function loadStats() {
    try {
      // TODO: Charger le solde (revenus et dépenses) depuis la base de données
      // TODO: Charger les totaux par catégorie depuis la base de données
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* TODO: Afficher le solde (revenus - dépenses) */}

      {/* TODO: Afficher les revenus et dépenses totales */}

      {/* TODO: Afficher la liste des dépenses par catégorie */}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  balanceCard: {
    backgroundColor: '#007AFF',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 20,
  },
  balanceLabel: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
  },
  balanceAmount: {
    color: 'white',
    fontSize: 36,
    fontWeight: 'bold',
    marginTop: 4,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  summaryLabel: {
    color: '#666',
    fontSize: 13,
  },
  summaryAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  categoryRow: {
    backgroundColor: 'white',
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 14,
    borderRadius: 10,
    marginBottom: 8,
  },
  categoryName: {
    fontSize: 15,
  },
  categoryAmount: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FF3B30',
  },
});
