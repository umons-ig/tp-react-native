# DevWallet

## Objectifs

Dans cet exercice, vous apprendrez à :

| Compétence | Description                                            |
| ---------- | ------------------------------------------------------ |
| SQLite     | Utiliser une base de données locale avec expo-sqlite   |
| CRUD       | Créer, lire et supprimer des données                   |
| SQL        | Écrire des requêtes avec SUM et GROUP BY               |

## Étape 0 : Lancer le projet

Commencez par naviguer vers le dossier de l'exercice et installer les dépendances :

```bash
cd 04-devwallet
npm install
```

Puis lancez le projet :

```bash
npx expo start
```

!!! info
    Si vous rencontrez des problèmes de connexion, essayez de lancer le projet avec le tunnel :

    ```bash
    npx expo start --tunnel
    ```

## Étape 1 : Compléter la base de données

Le fichier `lib/database.ts` contient la configuration de la base de données SQLite. La table `transactions` est déjà créée avec les colonnes suivantes :

| Colonne       | Type    | Description                          |
| ------------- | ------- | ------------------------------------ |
| `id`          | INTEGER | Identifiant unique (auto-incrémenté) |
| `amount`      | REAL    | Montant de la transaction            |
| `description` | TEXT    | Description de la transaction        |
| `category`    | TEXT    | Catégorie (Alimentation, Transport…) |
| `type`        | TEXT    | `'income'` ou `'expense'`            |
| `date`        | TEXT    | Date de la transaction               |

### 1.1 L'API expo-sqlite

L'API de `expo-sqlite` fournit deux méthodes principales pour interagir avec la base de données :

```typescript
// Lire des données (SELECT) — retourne un tableau de résultats
const rows = await database.getAllAsync<MonType>('SELECT * FROM table');

// Modifier des données (INSERT, UPDATE, DELETE) — utilise des paramètres ?
await database.runAsync('INSERT INTO table (col1, col2) VALUES (?, ?)', [val1, val2]);
```

!!! tip "Paramètres SQL"
    Les `?` dans les requêtes sont remplacés par les valeurs du tableau passé en second argument. Cela protège contre les injections SQL.

### 1.2 Fonctions à compléter

Chaque fonction doit d'abord récupérer la base de données avec `getDatabase()`, puis exécuter une requête SQL.

Voici un exemple complet pour la première fonction :

```typescript title="lib/database.ts"
export async function getTransactions(): Promise<Transaction[]> {
  const database = await getDatabase();
  return await database.getAllAsync<Transaction>(
    'SELECT * FROM transactions ORDER BY date DESC'
  );
}
```

!!! example "Tâche"
    En suivant le même pattern, complétez les 4 fonctions restantes :

    **`addTransaction()`** — Insérer une nouvelle transaction :
    ```sql
    INSERT INTO transactions (amount, description, category, type, date) VALUES (?, ?, ?, ?, ?)
    ```
    Utilisez `database.runAsync()` avec un tableau contenant les valeurs : `[transaction.amount, transaction.description, ...]`.

    **`deleteTransaction()`** — Supprimer une transaction par son id :
    ```sql
    DELETE FROM transactions WHERE id = ?
    ```

    **`getBalance()`** — Calculer le total par type (income/expense) :
    ```sql
    SELECT type, SUM(amount) as total FROM transactions GROUP BY type
    ```
    Cette requête retourne un tableau avec une entrée par type. Parcourez le résultat pour extraire le total de chaque type :
    ```typescript
    for (const row of result) {
      if (row.type === 'income') income = row.total;
      if (row.type === 'expense') expenses = row.total;
    }
    ```

    **`getTotalsByCategory()`** — Calculer le total des dépenses par catégorie :
    ```sql
    SELECT category, SUM(amount) as total FROM transactions WHERE type = 'expense' GROUP BY category ORDER BY total DESC
    ```

## Étape 2 : Liste des transactions

Dans `app/(tabs)/index.tsx`, on veut afficher la liste des transactions et permettre d'en ajouter de nouvelles.

!!! info "useFocusEffect"
    Contrairement à `useEffect` qui s'exécute une seule fois au montage, `useFocusEffect` s'exécute **à chaque fois que l'écran redevient visible** (par exemple quand on revient du formulaire d'ajout). C'est essentiel pour rafraîchir les données après un ajout.

    ```typescript
    useFocusEffect(
      useCallback(() => {
        // Ce code s'exécute à chaque fois que l'écran est affiché
        loadTransactions();
      }, [])
    );
    ```

!!! example "Tâche"
    Complétez le fichier `app/(tabs)/index.tsx` :

    1. Dans `loadTransactions()`, appelez `getTransactions()` et mettez à jour le state :
    ```typescript
    const data = await getTransactions();
    setTransactions(data);
    ```

    2. Dans `handleDelete()`, supprimez la transaction puis rechargez la liste :
    ```typescript
    await deleteTransaction(id);
    await loadTransactions();
    ```

    3. Dans le `SafeAreaView`, affichez les transactions avec une `FlatList` :
    ```typescript
    <FlatList
      data={transactions}
      keyExtractor={(item) => item.id.toString()}
      renderItem={({ item }) => (
        <TransactionCard transaction={item} onDelete={handleDelete} />
      )}
      ListEmptyComponent={<Text style={styles.empty}>Aucune transaction</Text>}
    />
    ```

    4. Sous la `FlatList`, ajoutez un bouton flottant (+) pour naviguer vers le formulaire :
    ```typescript
    <Pressable style={styles.fab} onPress={() => router.push('/new')}>
      <Text style={styles.fabText}>+</Text>
    </Pressable>
    ```

## Étape 3 : Le composant TransactionCard

Dans `components/TransactionCard.tsx`, le composant reçoit une transaction et un callback `onDelete`. Les styles sont déjà définis.

!!! example "Tâche"
    Complétez le composant `TransactionCard` à l'intérieur de la `View style={styles.card}` :

    1. Déclarez une constante pour savoir si c'est un revenu :
    ```typescript
    const isIncome = transaction.type === 'income';
    ```

    2. Ajoutez une `View` avec le style `info` contenant 3 `Text` :
        - `transaction.description` avec le style `styles.description`
        - `transaction.category` avec le style `styles.category`
        - `transaction.date` avec le style `styles.date`

    3. Affichez le montant avec la couleur qui dépend du type (vert pour revenu, rouge pour dépense) :
    ```typescript
    <Text style={[styles.amount, isIncome ? styles.income : styles.expense]}>
      {isIncome ? '+' : '-'}{transaction.amount.toFixed(2)} €
    </Text>
    ```

    4. Ajoutez un `Pressable` de suppression avec le style `deleteBtn` qui appelle `onDelete(transaction.id)` au `onPress`. Affichez le texte `×` avec le style `deleteText`.
        ```

## Étape 4 : Formulaire d'ajout

Dans `app/new/index.tsx`, on retrouve un formulaire pour ajouter une transaction. Les states (`amount`, `description`, `category`, `type`) et les styles sont déjà définis.

!!! example "Tâche"
    Complétez le formulaire dans le `SafeAreaView` :

    1. Ajoutez les boutons de type (Dépense / Revenu) dans une `View` avec le style `typeRow`. Chaque bouton est un `Pressable` qui change le state `type` :
    ```typescript
    <View style={styles.typeRow}>
      <Pressable
        style={[styles.typeBtn, type === 'expense' && styles.typeBtnActive]}
        onPress={() => setType('expense')}
      >
        <Text style={[styles.typeBtnText, type === 'expense' && styles.typeBtnTextActive]}>
          Dépense
        </Text>
      </Pressable>
      {/* Même chose pour 'income' avec le texte "Revenu" */}
    </View>
    ```

    2. Ajoutez deux `TextInput` pour le montant et la description :
    ```typescript
    <TextInput
      style={styles.input}
      placeholder="Montant"
      keyboardType="numeric"
      value={amount}
      onChangeText={setAmount}
    />
    ```
    Faites la même chose pour la description (sans `keyboardType`).

    3. Affichez les catégories avec un `.map()` sur le tableau `CATEGORIES`. Chaque catégorie est un `Pressable` qui met à jour le state `category` :
    ```typescript
    <Text style={styles.label}>Catégorie</Text>
    <View style={styles.categoriesGrid}>
      {CATEGORIES.map((cat) => (
        <Pressable
          key={cat}
          style={[styles.categoryBtn, category === cat && styles.categoryBtnActive]}
          onPress={() => setCategory(cat)}
        >
          <Text style={[styles.categoryBtnText, category === cat && styles.categoryBtnTextActive]}>
            {cat}
          </Text>
        </Pressable>
      ))}
    </View>
    ```

    4. Ajoutez un bouton de soumission et complétez `handleSubmit` :
    ```typescript
    <Pressable style={styles.submitBtn} onPress={handleSubmit}>
      <Text style={styles.submitBtnText}>Ajouter</Text>
    </Pressable>
    ```
    Dans `handleSubmit`, appelez `addTransaction()` avec un objet contenant `amount` (parsé en nombre), `description`, `category`, `type` et la date du jour, puis `router.back()`.

    !!! tip "Date du jour"
        Pour obtenir la date au format `YYYY-MM-DD` :
        ```typescript
        date: new Date().toISOString().split('T')[0]
        ```

## Étape 5 : Statistiques

Dans `app/(tabs)/stats.tsx`, on affiche un résumé des finances. Les styles sont déjà définis pour les cartes de solde, résumé et catégories.

!!! example "Tâche"
    Complétez la page de statistiques :

    1. Dans `loadStats()`, chargez les données depuis la base :
    ```typescript
    const balance = await getBalance();
    setIncome(balance.income);
    setExpenses(balance.expenses);

    const categories = await getTotalsByCategory();
    setCategoryTotals(categories);
    ```

    2. Avant le `return`, calculez le solde :
    ```typescript
    const balance = income - expenses;
    ```

    3. Affichez la carte du solde :
    ```typescript
    <View style={styles.balanceCard}>
      <Text style={styles.balanceLabel}>Solde</Text>
      <Text style={styles.balanceAmount}>{balance.toFixed(2)} €</Text>
    </View>
    ```

    4. Affichez les revenus et dépenses côte à côte dans une `View` avec le style `row`. Chaque côté est une `View` avec le style `summaryCard` contenant :
        - Un `Text` avec le style `summaryLabel` (texte "Revenus" ou "Dépenses")
        - Un `Text` avec le style `summaryAmount` et une couleur inline : `{ color: '#34C759' }` pour les revenus, `{ color: '#FF3B30' }` pour les dépenses

    5. Affichez les dépenses par catégorie avec un `.map()` :
    ```typescript
    <Text style={styles.sectionTitle}>Dépenses par catégorie</Text>
    {categoryTotals.map((cat) => (
      <View key={cat.category} style={styles.categoryRow}>
        <Text style={styles.categoryName}>{cat.category}</Text>
        <Text style={styles.categoryAmount}>-{cat.total.toFixed(2)} €</Text>
      </View>
    ))}
    ```
