---
sidebar_position: 4
title: "Exercice 3 : DevHub"
---

# DevHub

## 🎯 Objectifs

Dans cet exercice, vous apprendrez à :

| Compétence | Description                                            |
| ---------- | ------------------------------------------------------ |
| 🔐 Auth    | Implémenter l'authentification avec GitHub             |
| 📡 API     | Intégrer l'API GitHub et Supabase                      |
| 🔄 État    | Synchroniser les données entre le client et le serveur |

Voici à quoi ressemblera votre application finale :

<div style={{ display: 'flex', justifyContent: 'center', gap: '20px', margin: '20px 0' }}>
  <img
    src={require('/img/03-01-app.png').default}
    alt="DevHub App - Login"
    width={300}
  />
  <img
    src={require('/img/03-02-app.png').default}
    alt="DevHub App - Trending"
    width={300}
  />
</div>

## 📋 Étape 0 : Lancer le projet

Commencez par naviguer vers le dossier de l'exercice et installer les dépendances :

```bash
cd 03-devhub
npm install
```

Puis lancez le projet :

```bash
npx expo start
```

:::info
Si vous rencontrez des problèmes de connexion, essayez de lancer le projet avec le tunnel :

```bash
npx expo start --tunnel
```

:::

## 📋 Étape 1 : Créer un projet Supabase

### 1.1 Installation des dépendances

Naviguez vers le dossier de l'exercice et installez les dépendances.

```bash
cd exercises/03-devhub
npm install
```

### 1.2 Créer un projet Supabase

Créez un nouveau projet sur [Supabase](https://supabase.com) :

1. Connectez-vous à votre compte Supabase
2. Créez un nouveau projet
3. Notez l'URL et la clé d'API de votre projet

### 1.2 Variables d'environnement

Naviguez vers le dossier de l'exercice et installez les dépendances. Ensuite on va copier le fichier `.env.example` et le renommer en `.env`. C'est dans ce fichier que vous mettrez votre clé d'API Supabase.

```bash
cp .env.example .env
```

Ouvrez le fichier `.env` et remplacez les valeurs par vos propres valeurs.

```bash
EXPO_PUBLIC_SUPABASE_URL=
EXPO_PUBLIC_SUPABASE_ANON_KEY=
```

### 1.3 Gestion du Login et Register

Pour la gestion du login et register, nous allons utiliser le SDK de Supabase. Pour cela dans le dossier `lib` on va créer un fichier `supabase.ts` et on va y implémenter le SDK de Supabase. Dans ce dossier on retrouve nos variables d'environnement. Expo permet de faire appel à ces variables pour autant qu'elles possèdent le préfixe `EXPO_PUBLIC_`.

```typescript
import "react-native-url-polyfill/auto";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error("Missing Supabase environment variables");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

Maintenant qu'on a notre client Supabase, on va pouvoir l'utiliser dans notre application. Nous allons créer une page de login et de register dans le dossier `app/auth`.

Les deux pages auront un formulaire et un bouton pour se connecter ou se register (similaire à l'exercice 2). la nouveauté ici est que nous allons utiliser le SDK de Supabase pour gérer l'authentification.

La fonction SignUp ressemble a ceci. Il manque la partie ou on appelle le SDK de Supabase pour faire le SignUp. Pour cela regardez la documentation de [Supabase](https://supabase.com/docs/reference/javascript/auth-signup).

```typescript
async function signUp() {
  if (!email || !password) {
    Alert.alert("Error", "Please fill in all fields");
    return;
  }

  setLoading(true);
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (error) throw error;

    if (data.session) {
      router.replace("/(tabs)");
    } else {
      Alert.alert(
        "Success",
        "Registration successful. Please check your email.",
        [{ text: "OK", onPress: () => router.replace("/auth/login") }]
      );
    }
  } catch (error) {
    Alert.alert("Error", (error as Error).message);
  } finally {
    setLoading(false);
  }
}
```

Pour la fonction de connexion, il faut utiliser la fonction `signInWithPassword` de Supabase. Pour cela regardez la documentation de [Supabase](https://supabase.com/docs/reference/javascript/auth-signinwithpassword).

```typescript
async function signIn() {
  if (!email || !password) {
    Alert.alert("Error", "Please fill in all fields");
    return;
  }

  setLoading(true);
  try {
    // TODO: Ajouter la connexion avec le SDK de Supabase

    if (error) throw error;

    router.replace("/(tabs)");
  } catch (error) {
    Alert.alert("Error", (error as Error).message);
  } finally {
    setLoading(false);
  }
}
```

### 1.4 Gestion du Layout

L'application aura 2 layouts. Le layout qui se trouve dans le dossier `app` est le layout racine de l'application. Il est utilisé pour l'authentification et le layout `(tabs)/_layout.tsx` sera utilisé pour les onglets (trending et recherche).

Le premier layout est le suivant. Il permet de rediriger l'utilisateur vers la page de login si il n'est pas connecté et vers la page des onglets si il est connecté. Pour cela la variable session est utilisée.

```typescript
export default function RootLayout() {
  const [session, setSession] = useState<Session | null>(null);
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    //1. verifier si l'utilisateur est connecté
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    //2. écouter les changements d'état de la session
    supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
  }, []);

  useEffect(() => {
    const inAuthGroup = segments[0] === "auth";

    if (!session && !inAuthGroup) {
      router.replace("/auth/login");
    } else if (session && inAuthGroup) {
      router.replace("/(tabs)");
    }
  }, [session, segments]);

  return <Slot />;
}
```

Le deuxième layout est le suivant. Il permet de gérer les onglets (trending et recherche).

```typescript
export default function TabsLayout() {
  const router = useRouter();

  async function handleLogout() {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      router.replace("/auth/login");
    } catch (error) {
      Alert.alert("Error logging out", (error as Error).message);
    }
  }

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#007AFF",
        headerRight: () => (
          <TouchableOpacity onPress={handleLogout} style={{ marginRight: 16 }}>
            <Ionicons name="log-out-outline" size={24} color="#007AFF" />
          </TouchableOpacity>
        ),
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Trending",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="trending-up" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: "Search",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="search" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
```

## 🔐 Étape 2 : API GitHub

Dans la page Home, on affiche la liste des repositories trending. Pour cela on utilise l'API de GitHub. Dans le dossier `lib` on peut voir le fichier `github.ts` qui contient la configuration de l'API GitHub.

Dans ce dossier on retrouve les informations que l'on recupère:

```typescript
type Repository = {
  id: number;
  name: string;
  owner: {
    login: string;
  };
  description: string;
  stargazers_count: number;
  html_url: string;
};
```

Nous avons egalement deux fonctions qui permettent de récupérer les repositories trending et les repositories recherchés:

```typescript
export const github = {
  // Obtenir les repos tendance (limité à 30 résultats)
  getTrendingRepos: () =>
    fetchFromGitHub<Repository>(
      "/search/repositories?q=stars:>1&sort=stars&order=desc&per_page=30"
    ),

  // Rechercher des repos
  searchRepos: (query: string) =>
    fetchFromGitHub<Repository>(
      `/search/repositories?q=${encodeURIComponent(query)}&per_page=30`
    ),
};
```

### 2.1 Récupérer les repositories trending

Pour récupérer les repositories trending, on utilise la fonction `getTrendingRepos` qui fait une requête à l'API de GitHub. Dans le fichier `app/(tabs)/index.tsx` on peut voir la fonction `loadTrendingRepos` qui permet de récupérer les repositories trending.

```typescript
async function loadTrendingRepos() {
  try {
    // TODO: Récupérer les repositories trending
    // Mettre à jour la variable repos avec les repositories trending
  } catch (error) {
    console.error("Error:", error);
  } finally {
    setLoading(false);
  }
}
```

:::tip

Pour récupérer les repositories trending, on utilise la fonction `getTrendingRepos` qui fait une requête à l'API de GitHub. Ensuite il faut mettre à jour le useState `repos` avec les repositories trending.

:::

### 2.2 Afficher les repositories trending

Toujours dans le fichier `app/(tabs)/index.tsx` on peut voir la fonction `useRepos` qui permet de récupérer les repositories trending.

```typescript
return (
  <SafeAreaView style={styles.container}>
    // TODO: Afficher les repositories trending avec une FlatList
  </SafeAreaView>
);
```

:::tip

Pour afficher les repositories trending, on utilise une FlatList. Vous pouvez soit utiliser le composant `RepoCard` ou créer votre propre composant ou utiliser des variables Text et View.

:::

## 🔐 Étape 3 : Recherche de repositories

Similaire à l'étape 2, on va ajouter une fonction pour rechercher des repositories. Dans le fichier `app/(tabs)/search.tsx` on peut voir la fonction `searchRepos` qui permet de rechercher des repositories.

```typescript
export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(false);

  async function searchRepos() {
    if (!query.trim()) return;

    setLoading(true);
    try {
      // TODO: Rechercher des repositories avec la fonction `searchRepos`
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        value={query}
        onChangeText={setQuery}
        onSubmitEditing={searchRepos}
        placeholder="Search repositories..."
        returnKeyType="search"
      />
      {loading ? (
        <ActivityIndicator style={styles.center} size="large" />
      ) : (
        // TODO: Afficher les repositories recherchés avec une FlatList
      )}
    </View>
  );
}
```
