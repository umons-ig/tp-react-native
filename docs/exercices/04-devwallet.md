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

L'API de `expo-sqlite` fournit trois méthodes principales pour interagir avec la base de données :

```typescript
// Lire des données (SELECT) — retourne un tableau de résultats
const rows = await database.getAllAsync<MonType>('SELECT * FROM table');

// Modifier des données (INSERT, UPDATE, DELETE) — utilise des paramètres ?
await database.runAsync('INSERT INTO table (col1, col2) VALUES (?, ?)', [val1, val2]);
```

!!! tip "Paramètres SQL"
    Les `?` dans les requêtes sont remplacés par les valeurs du tableau passé en second argument. Cela protège contre les injections SQL.

### 1.2 Fonctions à compléter

!!! example "Tâche"
    Complétez les 5 fonctions dans `lib/database.ts` :

    - **`getTransactions()`** : récupérer toutes les transactions triées par date décroissante (`ORDER BY date DESC`).
    - **`addTransaction()`** : insérer une nouvelle transaction avec les 5 colonnes (amount, description, category, type, date).
    - **`deleteTransaction()`** : supprimer une transaction par son `id`.
    - **`getBalance()`** : calculer le total des revenus et des dépenses. Utilisez `SUM(amount)` combiné avec `GROUP BY type` pour obtenir un total par type.
    - **`getTotalsByCategory()`** : calculer le total des dépenses par catégorie. Filtrez uniquement les dépenses (`WHERE type = 'expense'`), puis regroupez par catégorie avec `GROUP BY`.

    !!! tip "Conseil pour getBalance()"
        La requête retourne un tableau avec une entrée par type. Parcourez le résultat pour extraire le total de chaque type :
        ```typescript
        for (const row of result) {
          if (row.type === 'income') income = row.total;
          if (row.type === 'expense') expenses = row.total;
        }
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

    - Dans `loadTransactions()`, appelez `getTransactions()` et mettez à jour le state avec `setTransactions`.
    - Dans `handleDelete()`, appelez `deleteTransaction(id)` puis rechargez la liste.
    - Affichez les transactions avec une `FlatList` et le composant `TransactionCard`.
    - Ajoutez un bouton flottant (+) qui navigue vers `/new` avec `router.push('/new')`.

    !!! tip "Conseil"
        Les styles `fab` et `fabText` sont déjà définis pour le bouton flottant.

## Étape 3 : Le composant TransactionCard

Dans `components/TransactionCard.tsx`, le composant reçoit une transaction et un callback `onDelete`. Les styles sont déjà définis.

!!! example "Tâche"
    Complétez le composant `TransactionCard` :

    - Créez une variable `isIncome` pour vérifier si `transaction.type === 'income'`.
    - Dans une `View` avec le style `info`, affichez la description, la catégorie et la date.
    - Affichez le montant avec un `+` pour les revenus et un `-` pour les dépenses.
    - Ajoutez un `Pressable` de suppression qui appelle `onDelete(transaction.id)`.

    !!! tip "Conseil"
        Utilisez la composition de styles pour changer la couleur du montant :
        ```typescript
        <Text style={[styles.amount, isIncome ? styles.income : styles.expense]}>
          {isIncome ? '+' : '-'}{transaction.amount.toFixed(2)} €
        </Text>
        ```

## Étape 4 : Formulaire d'ajout

Dans `app/new/index.tsx`, on retrouve un formulaire pour ajouter une transaction. Les states (`amount`, `description`, `category`, `type`) et les styles sont déjà définis.

!!! example "Tâche"
    Complétez le formulaire :

    - Ajoutez deux `Pressable` pour choisir le type (Dépense / Revenu). Utilisez `styles.typeBtn` et `styles.typeBtnActive` pour le style actif.
    - Ajoutez un `TextInput` pour le montant avec `keyboardType="numeric"`.
    - Ajoutez un `TextInput` pour la description.
    - Affichez les catégories (tableau `CATEGORIES`) avec un `.map()` sous forme de boutons sélectionnables.
    - Dans `handleSubmit`, appelez `addTransaction()` avec les valeurs du formulaire et la date du jour, puis `router.back()`.

    !!! tip "Date du jour"
        Pour obtenir la date au format `YYYY-MM-DD` :
        ```typescript
        date: new Date().toISOString().split('T')[0]
        ```

## Étape 5 : Statistiques

Dans `app/(tabs)/stats.tsx`, on affiche un résumé des finances. Les styles sont déjà définis pour les cartes de solde, résumé et catégories.

!!! example "Tâche"
    Complétez la page de statistiques :

    - Dans `loadStats()`, appelez `getBalance()` pour mettre à jour `income` et `expenses`, et `getTotalsByCategory()` pour `categoryTotals`.
    - Affichez le solde (revenus - dépenses) dans une `View` avec `styles.balanceCard`.
    - Affichez les revenus et dépenses totales côte à côte dans une `View` avec `styles.row`.
    - Affichez la liste des dépenses par catégorie avec un `.map()` sur `categoryTotals`.
