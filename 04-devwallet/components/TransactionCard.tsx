import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Transaction } from '../types';

type Props = {
  transaction: Transaction;
  onDelete: (id: number) => void;
};

export default function TransactionCard({ transaction, onDelete }: Props) {
  return (
    // TODO: Afficher les détails de la transaction (description, catégorie, montant, date)
    // TODO: Ajouter un bouton pour supprimer la transaction
    <View style={styles.card}>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 6,
    borderRadius: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  info: {
    flex: 1,
  },
  description: {
    fontSize: 16,
    fontWeight: '600',
  },
  category: {
    color: '#666',
    fontSize: 13,
    marginTop: 2,
  },
  date: {
    color: '#999',
    fontSize: 12,
    marginTop: 2,
  },
  amount: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  income: {
    color: '#34C759',
  },
  expense: {
    color: '#FF3B30',
  },
  deleteBtn: {
    marginLeft: 12,
    padding: 6,
  },
  deleteText: {
    color: '#FF3B30',
    fontSize: 18,
  },
});
