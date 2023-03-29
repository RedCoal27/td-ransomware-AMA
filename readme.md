# TP de Maillet Alexandre

Avant toute chose, j'ai modifié ajouté des dossier monté dans docker afin de test le chiffrement directement car le docker se ferme après l'execution du script et donc je ne peux pas voir le résultat du chiffrement.
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