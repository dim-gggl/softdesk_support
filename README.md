# <div align="center"> 🖇️ Soft Desk Support

## <div align="center"> API REST

## 1 - Clôner le Repo

Copiez/Collez la commande suivante dans votre terminal :
_(Pour clôner le projet et se placer à la racine)_
```bash
 git clone git@github.com:dim-gggl/softdesk_support.git
 cd SoftDesk_Support
```

## 2 - Environnement virtuel et Dépendances

Le projet a été initialisé avec `poetry` et l'environnement et les dépendances lui permettant de tourner peuvent donc facilement être installés avec la commande :

```bash
poetry install
```

puis en fonction de la version de `poetry`dont vous disposez :

```bash
poetry shell
```
mais cette commande est dépréciée, alors :
```bash
eval $(poetry env activate)
```

Si vous n'avez pas `poetry`, il est toujours possible d'installer votre environnement virtuel et d'installer les dépendances via le fichier `requirements.txt` :
```bash
python3 -m venv .venv
pip install --upgrade pip
pip install -r requirements.txt
```
---
## 3 - Variable d'enironnement
Pour éviter de harcoder la secret key de Django, cette dernière a été placée dans le fichier `.env` à la racine du projet.
Il est possible de l'afficher facilement afin de la copier à l'aide de la commande suivante :
```bash
cat .env
```
Copiez la clé, puis:
```bash
export DJANGO_SECRET_KEY= # Collez-la ici
```
## 4 - Lancement du serveur
Tout est prêt maintenant pour tester le fonctionnement de l'API.

```bash
python3 src/manage.py runserver
```
Si votre terminal affiche :
```bash
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 12, 2025 - 18:29:59
Django version 5.2.3, using settings 'soft_desk_support.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead.
For more information on production servers see: https://docs.djangoproject.com/en/5.2/howto/deployment/
```
C'est que tout fonctionne.

## 5 - Fonctionnement de l'API

Dans un premier temps, il faut récupérer un `token` afin d'avoir accès aux informations.

Pour ça, 2 options:

### 1. Vous inscrire sur la plateforme de Soft Desk

Pour se faire, personnalisez le profil suivant :
```json
{
    "username": "<VOTRE PSEUDO>",
    "password": "<VOTRE MOT DE PASSE>",
    "age": 15,                   // 15 ans est l'âge minimum requis pour l'app
    "can_be_contacted": false,   // Remplacer par false si vous ne souhaitez pas être contacté(e)
    "can_data_be_shared": false, // Idem si vous ne souhaitez pas que vos données soient partagées avec des entreprises tierces
}
```
Et l'envoyer à l'API.
par cURL:
```bash
curl -X POST "http://127.0.0.1:8000/api/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "VOTRE_PSEUDO",
       "password": "VOTRE_MOT_DE_PASSE",
       "age": 15,
       "can_be_contacted": true,
       "can_data_be_shared": true
     }
```
ou par POSTMAN par exemple.

Il suffit d'intégrer ce `JSON` dans le corps de la requête `POST` et de l'envoyer à `http://127.0.0.1:8000/api/users/`

### 2 - Utiliser ce profil générique

```json
{
    "username": "user_6",
    "password": "azer"
}
```

envoyez ce `JSON` ou les mêmes infos concernant votre profil personnalisé dans le corps d'une requête `POST`, cette fois-ci à l'adresse `http://127.0.0.1:8000/api/token/`

La réponse contiendra votre `token` estampillé `access`, qu'il ne vous restera plus qu'à copier (et stocker précieusement en lieu sûr) et à l'ajouter en `header` de vos futures requêtes à l'API sous la clé `Authorization`

Ex:
```json
{
    "Authorization": "Bearer <LE CODE>..."
}
```

## 6 - Les Ressources

### -- USERS --

Il est possible d'afficher la liste de tous les utilisateurs inscrits :

| ENDPOINT | GET | POST | DELETE |
|:-:|:-:|:-:|:-:|
|`api/users/`|Liste de tous les utilisateurs inscrits. | Crée un nouvel utilidateur | `405 NOT ALLOWED` |
| `api/users/<int:user_id>/` | Affiche les détails d'un utilisateur | `405 NOT ALLOWED` | Supprime l'utilisateur (Si la requête provient de l'utilisateur lui-même ou d'un membre admin)



---
### Et quelques filtres utiles pour l'affichage des listes :

| Filtres | Actions |
|---|:-:|
|`?username=<USERNAME>`| Pour chercher un utilisateur précis. |
|`?id=<USER_ID>` | Idem via le numéro ID. |
| `?contact_ok=true` | Pour afficher uniquement les utilisateurs acceptant d'être contactés. |
| `?data_shared_ok=true` | Pour voir ceux qui acceptent que leurs données soient partagées |

---

### -- PROJECTS --

Comme pour les utilisateurs, les projets peuvent être affichés sous forme de liste, ou individuellement, avec leurs informations détaillées.

| ENDPOINT | GET | POST | DELETE |
|:-:|:-:|:-:|:-:|
|`api/projects/`| Liste de tous les projets suavegardés | Créations d'un nouveau projet |  `405 NOT ALOWED` |
| `api/projects/<int:project_id>/` | Affiche les détails d'un projet | `405 NOT ALLOWED` | Supprime le projet (Si la requête provient de l'auteur du projet ou d'un membre admin)

```python
# ================================
#          À SUIVRE
# ================================
```
