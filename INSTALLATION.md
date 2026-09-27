# Installer LithoShape3D en 1 minute

LithoShape3D n'est pas encore « signé » auprès d'Apple et de Microsoft.
Au **premier lancement seulement**, votre ordinateur affiche donc un avertissement.
C'est normal : il suffit de l'autoriser une fois, en suivant l'une des deux méthodes ci-dessous.

LithoShape3D fonctionne **entièrement sur votre ordinateur**.
Aucune photo ni donnée n'est envoyée sur internet.

---

## 🍎 Mac (Apple Silicon : M1, M2, M3, M4)

1. Téléchargez le fichier `LithoShape3D-macOS-….zip`, puis double-cliquez dessus pour le décompresser.
2. Glissez **LithoShape3D** dans le dossier **Applications**.
3. Double-cliquez sur LithoShape3D.
   Un message indique qu'Apple ne peut pas vérifier l'application : cliquez sur **OK** (ou **Terminé**).
4. Ouvrez **Réglages Système → Confidentialité et sécurité**, puis descendez en bas de la page.
   À côté de « LithoShape3D a été bloquée… », cliquez sur **Ouvrir quand même**.
   Confirmez avec votre mot de passe ou Touch ID.
5. C'est terminé : LithoShape3D s'ouvre désormais normalement, comme n'importe quelle application.

**Si macOS dit « LithoShape3D est endommagé et ne peut pas être ouvert »**, l'application n'est pas abîmée :
macOS bloque simplement les fichiers téléchargés qui ne sont pas signés.
1. Ouvrez l'application **Terminal** (Applications → Utilitaires).
2. Copiez-collez cette ligne, puis appuyez sur Entrée :

   ```
   xattr -dr com.apple.quarantine /Applications/LithoShape3D.app
   ```

3. Relancez LithoShape3D.

---

## 🪟 Windows 10 / 11

1. Téléchargez `LithoShape3D-Setup-….exe`, puis double-cliquez dessus.
2. Si un écran bleu « **Windows a protégé votre ordinateur** » apparaît :
   cliquez sur **Informations complémentaires**, puis sur **Exécuter quand même**.
3. Suivez l'installation (Suivant → Installer → Terminer).

**Si votre antivirus bloque le fichier**, c'est une fausse alerte fréquente avec les logiciels récents non signés.
Autorisez LithoShape3D dans votre antivirus, ou signalez-le-nous.

---

## 🔑 Activer votre licence

Ouvrez le menu **Aide → Licence**, collez la clé reçue par e-mail, puis validez.
Tout le reste est gratuit à essayer : la licence ne sert qu'à **créer les fichiers d'impression**.

## 🧠 Option : détourage automatique des photos

Le premier clic sur **« Détourer la photo »** propose de télécharger le modèle de détourage (environ 180 Mo, une seule fois).
Ensuite, tout fonctionne hors ligne. Vos photos ne quittent jamais votre ordinateur.

## ❓ Besoin d'aide

Décrivez votre problème dans l'onglet **Issues** du dépôt
[LithoShape3D-releases](https://github.com/le-belge/LithoShape3D-releases/issues),
en précisant votre système (Mac ou Windows) et la version (menu **Aide → À propos**).
