# TP de Maillet Alexandre

## Comment utiliser
Pour ce code, la console doit être executé dans le dossier TD. 

Dans un premier temps il faut lancer ./run_cnc.sh afin de démarer le serveur cnc.
Ensuite on peut créer différents fichier txt dans le dossier some_data afin de voir que le chiffrement a fonctionné.

Pour lancer le chiffrement, il faut lancer ./run_ransomware.sh dans un autre terminal. Cela va chiffrer les données de la victime (ici visible dans le dossier some_data)
Et tous les fichier txt sont également enregistré dans le dossier cnc en plus des informations sur la clé de chiffrement.

Une fois le rançomware lancé, impossible d'en sortir à moins de payer la rançon! Le prix double toute les 30s alors il faut faire vite!

L'attaquant peut retrouver la clé de la victime simplement en lançant read_key.py . Ce programme demande alors le token de la victime et donne la clé de chiffrement en base64. La victime peut alors rentrer cette clé pour retrouver ses fichiers si il à bien payé le prix correspondant.

Une version amélioré utilisant un Packer et un Dropper est également utilisable. Il faut packer le code en faisant

    -pyinstaller --onefile sources/ransomware.py

Et à ce moment la, au lieu de lancer le run_ransomware.sh, on peut lancer le dropper.sh
Le code va alors venir télécharger le fichier obfusqué à l'aide d'une clé et un xor. Pour ensuite l'executer directement le code téléchargé sur la machine de la victime!

## Question 1
L'algorithme de chiffrement utilisé dans le code fourni est appelé XOR (eXclusive OR). Il s'agit d'un algorithme de chiffrement symétrique simple et basique.
Cette algorithme n'est pas robuste pour plusieurs raisons:
- Prévisibilité : Si la clé ou une partie de la clé est connue ou devinée, il devient très facile de déchiffrer les données. La sécurité de l'algorithme repose entièrement sur la clé, ce qui le rend vulnérable aux attaques par force brute ou par recherche exhaustive de clés.
- Répétition de la clé : Dans le code fourni, la clé est répétée pour correspondre à la longueur des données. Cela rend l'algorithme vulnérable aux attaques statistiques, en particulier si les données sont plus longues que la clé et présentent des motifs reconnaissables.
- Absence de diffusion : L'algorithme XOR n'offre aucune diffusion des données, ce qui signifie que les modifications d'un seul caractère dans les données d'entrée n'affectent que le caractère correspondant dans les données chiffrées. Cela facilite l'analyse des données chiffrées et la détection de modèles.

En conclusion, l'algorithme XOR ne convient pas pour garantir la sécurité des données sensibles et ne doit pas être utilisé dans des applications de chiffrement où la confidentialité est cruciale.


## Question 2
Hacher le sel et la clé directement ne serait pas une bonne idée, car les fonctions de hachage sont conçues pour être rapides. Les attaquants pourraient facilement lancer des attaques par force brute pour deviner la clé. De plus, les fonctions de hachage ne sont pas conçues pour être utilisées comme des fonctions de dérivation de clés.

Le HMAC (Hash-based Message Authentication Code) est une construction cryptographique utilisée pour vérifier l'intégrité des données et l'authenticité d'un message. Bien que le HMAC utilise une fonction de hachage, il ne s'agit pas d'une fonction de dérivation de clés.

En utilisant PBKDF2 (Password-Based Key Derivation Function 2), on peut améliorer la sécurité de la dérivation de clés en ajoutant un sel (pour éviter les attaques par table arc-en-ciel) et un grand nombre d'itérations (pour ralentir les attaques par force brute). PBKDF2 utilise également une fonction de hachage (comme SHA256) en interne, mais elle est conçue pour la dérivation de clés à partir de données secrètes (comme un mot de passe ou une clé).

## Question 3
Il est préférable de vérifier qu'un fichier token.bin n'est pas déjà présent pour plusieurs raisons :

Éviter d'écraser un token existant : Si un fichier token.bin existe déjà, cela signifie que le système a déjà été infecté et qu'un token a été généré. En écrasant ce fichier, nous perdons le token précédent, ce qui pourrait rendre impossible la récupération des données cryptées avec ce token.

Éviter de générer et d'envoyer des éléments cryptographiques inutiles : Si un fichier token.bin existe déjà, cela signifie que les éléments cryptographiques ont déjà été générés et envoyés au CNC. En vérifiant l'existence de ce fichier, nous évitons de générer et d'envoyer des éléments cryptographiques supplémentaires, ce qui pourrait encombrer le CNC et rendre le processus de récupération des données plus difficile.

Éviter de consommer des ressources inutilement : La génération des éléments cryptographiques et l'envoi au CNC consomment des ressources (CPU, mémoire, bande passante). En vérifiant l'existence d'un fichier token.bin, nous économisons ces ressources en évitant de répéter ces opérations inutilement.

## Question 4
On peut vérifier que la clé rentré est bonne en faisant une dérivation de la clé avec le sel et en vérifiant que le résultat est égale au token enregistré. Si c'est le cas, on peut alors déchiffrer les données.


# Bonus
## Question 1
Pour les fichier, avant de les chiffrer j'envois les données au cnc et je les enregistre dans leur emplacement équivalent dans le dossier où les token sont également enregistré.

## Question 2
Pour casser ce ransomware et récupérer la clé de chiffrement, il est possible d'exploiter la faiblesse de l'algorithme de chiffrement XOR utilisé. L'opération XOR possède une propriété particulière : si vous avez deux fichiers A et B, et que le fichier A est le résultat du chiffrement XOR du fichier B avec une clé K, alors en appliquant à nouveau l'opération XOR entre A et B, vous obtiendrez la clé K.

## Question 3
La bibliothèque cryptography offre plusieurs options de chiffrement fiables et largement utilisées. Parmi ces options, on trouve le chiffrement symétrique (AES) et le chiffrement asymétrique (RSA). Pour ce ransomware, le chiffrement symétrique AES à été utilisé.

## Question 4/5

Pour créer un binaire autonome à l'aide de PyInstaller, il suffit de lancer la commande suivante :

    -pyinstaller --onefile sources/ransomware.py

Cela va créer un dossier dist qui contient le binaire autonome ransomware . Pour lancer le binaire, il suffit de lancer ./run_compile_ransomware.sh dans un terminal.

