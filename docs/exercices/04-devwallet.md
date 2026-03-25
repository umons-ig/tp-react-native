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

    1. Dans `loadTransactions()`, appelez `getTransactions()` et mettez à jour le state avec `setTransactions`.
    2. Dans `handleDelete()`, appelez `deleteTransaction(id)` puis rechargez la liste avec `loadTransactions()`.
    3. Dans le `SafeAreaView`, affichez les transactions avec une `FlatList`. Passez le composant `TransactionCard` dans `renderItem` en lui passant la transaction et `handleDelete` en props.
    4. Ajoutez un bouton flottant (`Pressable` avec les styles `fab`/`fabText`) qui navigue vers `/new` avec `router.push('/new')`.

## Étape 3 : Le composant TransactionCard

Dans `components/TransactionCard.tsx`, le composant reçoit une transaction et un callback `onDelete`. Les styles sont déjà définis.

!!! example "Tâche"
    Complétez le composant `TransactionCard` à l'intérieur de la `View style={styles.card}` :

    1. Déclarez une constante `isIncome` qui vaut `true` si `transaction.type === 'income'`.
    2. Ajoutez une `View` (style `info`) contenant 3 `Text` : la description, la catégorie et la date (les styles correspondants existent déjà).
    3. Affichez le montant avec la couleur qui dépend du type. Utilisez la composition de styles :
    ```typescript
    <Text style={[styles.amount, isIncome ? styles.income : styles.expense]}>
      {isIncome ? '+' : '-'}{transaction.amount.toFixed(2)} €
    </Text>
    ```
    4. Ajoutez un `Pressable` de suppression (style `deleteBtn`) qui appelle `onDelete(transaction.id)`.

## Étape 4 : Formulaire d'ajout

Dans `app/new/index.tsx`, on retrouve un formulaire pour ajouter une transaction. Les states (`amount`, `description`, `category`, `type`) et les styles sont déjà définis.

!!! example "Tâche"
    Complétez le formulaire dans le `SafeAreaView` :

    1. Ajoutez deux `Pressable` dans une `View` avec le style `typeRow` pour choisir entre "Dépense" et "Revenu". Utilisez la composition de styles pour le bouton actif :
    ```typescript
    <Pressable
      style={[styles.typeBtn, type === 'expense' && styles.typeBtnActive]}
      onPress={() => setType('expense')}
    >
      <Text style={[styles.typeBtnText, type === 'expense' && styles.typeBtnTextActive]}>
        Dépense
      </Text>
    </Pressable>
    ```
    Faites la même chose pour `'income'` avec le texte "Revenu".

    2. Ajoutez deux `TextInput` (style `input`) : un pour le montant avec `keyboardType="numeric"`, un pour la description. Liez-les aux states avec `value` et `onChangeText`.

    3. Affichez les catégories avec un `.map()` sur le tableau `CATEGORIES` dans une `View` avec le style `categoriesGrid`. Chaque catégorie est un `Pressable` (même pattern de styles actifs que les boutons de type) qui appelle `setCategory(cat)`.

    4. Ajoutez un `Pressable` (style `submitBtn`) qui appelle `handleSubmit`. Dans `handleSubmit`, appelez `addTransaction()` avec un objet contenant les valeurs du formulaire et la date du jour, puis `router.back()`.

    !!! tip "Date du jour"
        Pour obtenir la date au format `YYYY-MM-DD` :
        ```typescript
        date: new Date().toISOString().split('T')[0]
        ```

## Étape 5 : Statistiques

Dans `app/(tabs)/stats.tsx`, on affiche un résumé des finances. Les styles sont déjà définis pour les cartes de solde, résumé et catégories.

!!! example "Tâche"
    Complétez la page de statistiques :

    1. Dans `loadStats()`, appelez `getBalance()` pour mettre à jour les states `income` et `expenses`, et `getTotalsByCategory()` pour `categoryTotals`.
    2. Avant le `return`, calculez le solde : `const balance = income - expenses`.
    3. Affichez le solde dans une `View` (style `balanceCard`) avec deux `Text` : le label "Solde" et le montant formaté avec `.toFixed(2)`.
    4. Affichez les revenus et dépenses côte à côte dans une `View` (style `row`). Chaque côté est une `View` (style `summaryCard`) avec un label et un montant. Utilisez une couleur inline pour différencier : `{ color: '#34C759' }` pour les revenus, `{ color: '#FF3B30' }` pour les dépenses.
    5. Affichez les dépenses par catégorie avec un `.map()` sur `categoryTotals`. Chaque entrée est une `View` (style `categoryRow`) avec le nom de la catégorie et son total.
