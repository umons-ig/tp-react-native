import { useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { addTransaction } from '../../lib/database';

const CATEGORIES = ['Alimentation', 'Transport', 'Loisirs', 'Logement', 'Salaire', 'Autre'];

export default function NewTransactionScreen() {
  const router = useRouter();
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Autre');
  const [type, setType] = useState<'income' | 'expense'>('expense');

  async function handleSubmit() {
    if (!amount || !description) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      Alert.alert('Erreur', 'Montant invalide');
      return;
    }

    try {
      // TODO: Ajouter la transaction dans la base de données avec addTransaction
      // TODO: Revenir à l'écran précédent avec router.back()
    } catch (error) {
      Alert.alert('Erreur', 'Impossible d\'ajouter la transaction');
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* TODO: Ajouter les boutons pour choisir le type (Dépense / Revenu) */}

      {/* TODO: Ajouter un TextInput pour le montant (clavier numérique) */}

      {/* TODO: Ajouter un TextInput pour la description */}

      {/* TODO: Afficher les catégories comme boutons sélectionnables */}

      {/* TODO: Ajouter un bouton pour soumettre le formulaire */}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  typeRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  typeBtn: {
    flex: 1,
    padding: 12,
    borderRadius: 10,
    backgroundColor: '#e0e0e0',
    alignItems: 'center',
  },
  typeBtnActive: {
    backgroundColor: '#007AFF',
  },
  typeBtnText: {
    fontWeight: '600',
    color: '#333',
  },
  typeBtnTextActive: {
    color: 'white',
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 14,
    fontSize: 16,
    marginBottom: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 8,
  },
  categoriesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 24,
  },
  categoryBtn: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#e0e0e0',
  },
  categoryBtnActive: {
    backgroundColor: '#007AFF',
  },
  categoryBtnText: {
    color: '#333',
    fontSize: 13,
  },
  categoryBtnTextActive: {
    color: 'white',
  },
  submitBtn: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  submitBtnText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
