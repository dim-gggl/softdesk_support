# <div align="center"> 🖇️ Soft Desk Support

## <div align="center"> API REST

## 1 - Clôner le Repo

Copiez/Collez la commande suivante dans votre terminal :
*(Pour clôner le projet et se placer à la racine)*

```bash
git clone https://github.com/dim-gggl/softdesk_support.git
cd softdesk_support
```

## 2 - Environnement virtuel et Dépendances

Le projet a été initialisé avec `poetry` et l'environnement et les dépendances lui permettant de tourner peuvent donc facilement être installés avec la commande :

```bash
poetry install
```

puis en fonction de la version de `poetry` dont vous disposez :

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
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3 - Variable d'environnement

Pour éviter de harcoder la secret key de Django, cette dernière a été placée dans le fichier `.env` à la racine du projet.
Il est possible de l'afficher facilement afin de la copier à l'aide de la commande suivante :

```bash
cat .env
```

Copiez la clé, puis:

```bash
export DJANGO_SECRET_KEY=<VOTRE_SECRET_KEY>
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
"username": "<VOTRE_PSEUDO>",
"password": "<VOTRE_MOT_DE_PASSE>",
"age": 15, // 15 ans est l'âge minimum requis pour l'app
"can_be_contacted": false, // Remplacer par false si vous ne souhaitez pas être contacté(e)
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
 }'
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

```http
Authorization: Bearer <VOTRE_TOKEN>
```

## 6 - Les Ressources

### -- USERS --

Il est possible d'afficher la liste de tous les utilisateurs inscrits :

| ENDPOINT | GET | POST | DELETE |
| :-: | :-: | :-: | :-: |
|`api/users/` | Liste de tous les utilisateurs inscrits. | Crée un nouvel utilisateur | `405 NOT ALLOWED` |
| `api/users/<int:id>/` | Détails d’un utilisateur (self ou admin) |`405 NOT ALLOWED` | Supprime son compte\* |

\*Suppression possible uniquement par l’utilisateur lui-même ou un admin.

#### Filtres utiles :

| Filtre | Description |
| :-- | :-- |
| `?username=<USERNAME>` | Récupérer un utilisateur par son pseudo. |
|`?id=<USER_ID>` | Récupérer un utilisateur par son ID. |
| `?contact_ok=true/false` | Filtrer selon consentement à être contacté.|
| `?data_shared_ok=true/false` | Filtrer selon consentement au partage des données. |

---

### -- PROJECTS --

| ENDPOINT | GET | POST | DELETE |
| :-: | :-: | :-: | :-: |
|`api/projects/` | Liste des projets où vous êtes membre. | Crée un nouveau projet. |`405 NOT ALLOWED`|
| `api/projects/<int:project_id>/` | Détails du projet (auteur, type, etc.) |`405 NOT ALLOWED`| Supprime (auteur/admin) |

| Filtre | Description |
| :-- | :-- |
| `name` | Filtrer par nom du projet|
| `author__username` | Filtrer par nom d'utilisateur de l'auteur |
| `type` | Filtrer par type de projet|
| `id` | Filtrer par identifiant du projet |

*Seuls les contributeurs peuvent consulter ces endpoints.*

### -- CONTRIBUTORS (Contributeurs) --

| ENDPOINT | GET | POST | DELETE |
| :-: | :-: | :-: | :-: |
|`api/projects/{project_id}/contributors/` |Liste des membres du projet. | Ajoute un contributeur\* | `405 NOT ALLOWED`|
| `api/projects/{project_id}/contributors/{id}/` | Détails d’une contribution (utilisateur). | `405 NOT ALLOWED`| Retire un contributeur\* |

| Filtre | Description |
| :-- | :-- |
| `is_author` | Filtrer par statut d'auteur (True/False) |
| `username`| Filtrer par nom d'utilisateur |
| `id`| Filtrer par identifiant|

*Seul l’auteur du projet peut ajouter ou supprimer un contributeur.*

### -- ISSUES (Tickets) --

|ENDPOINT|GET|POST|DELETE|
|:-:|:-:|:-:|:-:|
|`api/projects/{project_id}/issues/`|Liste des issues (paginated).|Crée une issue\*|`405 NOT ALLOWED`|
|`api/projects/{project_id}/issues/{issue_id}/`|Détails de l’issue (statut, assignee, etc.)|`405 NOT ALLOWED`|Supprime une issue\*|

**Quelques filtres**

| Filtre | Description |
| :-- | :-- |
| `priority` | Priorité du ticket |
| `label` | Étiquette associée |
| `status` | Statut du ticket |
| `assignee_id` | Identifiant de l'assigné |
| `is_finished` | Indique si le ticket est terminé |
| `to_do` | Indique si le ticket est à faire |
| `urgent` | Indique si le ticket est urgent |

*Tous les contributeurs peuvent créer et consulter ; seuls les auteurs peuvent modifier/supprimer une issue.*

### -- COMMENTS (Commentaires) --

| ENDPOINT | GET | POST | DELETE |
| :-: | :-: | :-: | :-: |
|`api/projects/{project_id}/issues/{issue_id}/comments/` |Liste des commentaires.| Ajoute un commentaire\* | `405 NOT ALLOWED` |
| `api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/` | Détails d’un commentaire. |`405 NOT ALLOWED`| Supprime un commentaire\* |



*Tous les contributeurs peuvent commenter ; seuls les auteurs de commentaires peuvent les supprimer.*

## 7 - Pagination

Toutes les listes (projects, issues, comments) sont paginées par défaut (5 éléments par page).
Vous pouvez ajuster via les paramètres `?limit=<n>&offset=<m>`.


```python
# =====================================
#              À SUIVRE
# =====================================
````


