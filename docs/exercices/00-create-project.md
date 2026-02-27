# Créer un projet

## Objectifs

Dans ce premier exercice, vous apprendrez à :

| Compétence      | Description                               |
| --------------- | ----------------------------------------- |
| Installation    | Créer un nouveau projet Expo React Native |
| Dépendances     | Gérer les dépendances avec npm            |
| Déploiement     | Lancer et tester votre application        |

## Étape 1: Créer un nouveau projet

Avant que vous avez remplis les prerequis.

Utilisez la commande suivante pour créer un nouveau projet :

```bash
npx create-expo-app@latest [nom-du-projet]
```

## Étape 2 : Installer les dépendances

Naviguez vers le dossier du projet et installez les dépendances :

```bash
cd [nom-du-projet]
npm install
```

## Étape 3 : Lancer le projet

Pour lancer le projet, utilisez la commande suivante. Assurez-vous que votre ordinateur et votre appareil mobile sont connectés au même réseau Wi-Fi.

```bash
npx expo start
```

!!! tip "Résolution des problèmes"
    Si vous rencontrez des problèmes de connexion, essayez :

    ```bash
    npx expo start --tunnel
    ```

    Cette commande créera un tunnel permettant d'accéder à votre projet depuis votre appareil mobile, même sur un réseau différent.
