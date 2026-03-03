# Prérequis

Avant de commencer les exercices, assurez-vous d'avoir installé les outils et logiciels suivants sur votre machine.

## Logiciels requis

### Node.js

Vérifiez que vous avez bien la version 22 ou une version supérieure installée:

```bash
node -v
```

Si vous n'avez pas Node.js installé, vous pouvez le télécharger [ici](https://nodejs.org/en/download).

#### Installation sur Windows

Installez [`fnm`](https://github.com/Schniz/fnm) (Fast Node Manager) via PowerShell :

```powershell
# Install fnm (Fast Node Manager):
winget install Schniz.fnm

# Set up fnm in PowerShell profile:
if (-not (Test-Path $profile)) { New-Item $profile -Force }
Add-Content $profile 'fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression'

# Reload profile:
. $profile

# Download and install Node.js:
fnm install 22

# Verify the Node.js version:
node -v # Should print "v22.22.0".

# Verify npm version:
npm -v # Should print "10.9.4".
```

#### Installation sur macOS

Installez `nvm` (Node Version Manager) :

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22

# Verify the Node.js version:
node -v # Should print "v22.22.0".

# Verify npm version:
npm -v # Should print "10.9.4".
```

### Git

Assurez-vous d'avoir Git installé. Si ce n'est pas le cas, vous pouvez l'installer [ici](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

```bash
git --version
```

### Environnement de développement React Native

En fonction de votre système d'exploitation, vous devrez installer différents outils. Suivez les instructions [ici](https://docs.expo.dev/get-started/set-up-your-environment/).

Pour ce workshop, nous utiliserons Expo. Installez l'application Expo Go sur votre téléphone.

### Clonage du projet

Clonez le projet avec la commande suivante:

```bash
git clone https://github.com/umons-ig/tp-react-native.git
```

Ouvrez le projet avec votre environnement de développement React Native.

```bash
cd tp-react-native
```

Pour fork le projet:

```bash
git remote -v
```
