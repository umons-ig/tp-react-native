import { FlatList, StyleSheet, Pressable, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link, useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import NoteCard from '../components/NoteCard';
import EventEmitter from 'eventemitter3';
import { Note } from '../types';

const initialNotes: Note[] = [
  {
    id: "1",
    title: "React Native Setup",
    content: "Install Node.js, then run npx create-expo-app",
    date: "2024-01-15",
  },
  {
    id: "2",
    title: "Git Commands",
    content: "git add, git commit, git push",
    date: "2024-01-16",
  },
];

// Event pour communiquer entre les écrans
export const addNoteEvent = new EventEmitter();

export default function Home() {
  const [notes, setNotes] = useState<Note[]>(initialNotes);

  useEffect(() => {
    // Définir la fonction de callback
    const handleNewNote = (note: Omit<Note, 'id' | 'date'>) => {
      const newNote = {
        ...note,
        id: Date.now().toString(),
        date: new Date().toISOString().split('T')[0],
      };
      setNotes(prev => [...prev, newNote]);
    };

    // Ajouter le listener
    addNoteEvent.on('newNote', handleNewNote);

    // Cleanup : retirer le listener
    return () => {
      addNoteEvent.removeListener('newNote', handleNewNote);
    };
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      {/* TODO: Ajouter un composant NoteCard pour chaque note */}
      {/* TODO: Ajouter un bouton pour créer une nouvelle note */}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#007AFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  fabText: {
    fontSize: 24,
    color: 'white',
  },
});