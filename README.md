![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdim-gggl%2Fsoftdesk_support%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![Static Badge](https://img.shields.io/badge/poetry-2.1.3-yellow)
![Static Badge](https://img.shields.io/badge/django-5.2.3-orange)
![Static Badge](https://img.shields.io/badge/DRF-3.16.0-pink)
![Static Badge](https://img.shields.io/badge/api-REST-green)


# <div align="center"> 🇬🇧 Soft Desk Support 🖇️

## <div align="center"> REST API

Soft Desk Support is a RESTful issue-tracking API that helps teams manage software development projects. Users can sign up and create projects, add other members as contributors, report issues (tickets) within those projects, and discuss solutions through comments. The application runs on **Python 3.11+** and is built with Django REST Framework.

All endpoints are secured via **JSON Web Tokens (JWT)** – apart from registration and login, a valid token must be provided in the request headers. Strict permission rules ensure that only project contributors can access a project’s data, and only the author of a resource (or an admin) can modify or delete it. The design follows GDPR guidelines: users must be at least 15 years old to register, and they can opt in/out of being contacted or having their data shared. Users may also update or delete their own account (right to rectification and erasure of personal data). Finally, following *green code* best practices, all list endpoints are paginated (5 items per page by default) to minimize unnecessary server load.

## 1 – Clone the Repo

Copy/Paste the following command into your terminal:
*(To clone the project and move to the root folder)*

```bash
git clone https://github.com/dim-gggl/softdesk_support.git  
cd softdesk_support
```

## 2 – Virtual Environment & Dependencies

The project was initialised with `poetry`, so the environment and all the dependencies can be installed with one command:

```bash
poetry install
```

Then, depending on the version of `poetry` you have:

```bash
poetry shell
```

> **Heads‑up** – this command is deprecated, so prefer:

```bash
eval $(poetry env activate)
```

If you don’t have `poetry`, you can still create a virtual environment and install the dependencies via `requirements.txt`:

```bash
python3 -m venv .venv  
source .venv/bin/activate  
pip install --upgrade pip  
pip install -r requirements.txt
```

---

## 3 – Environment Variable

The SECRET_KEY is already automatically loaded as soon as the environment is activated. If it wasn't though, you can follow the instructions below:

To avoid hard‑coding the Django secret key, it’s stored in the `.env` file at the project root. You can display it easily and copy it with:

```bash
cat .env
```

Copy the key, then export it:

```bash
export DJANGO_SECRET_KEY=<THE_SECRET_KEY>
```

## 4 – Start the Server

Everything’s set up – time to test the API.

```bash
python3 src/manage.py runserver
```

If your terminal prints something like:

```bash
Watching for file changes with StatReloader  
Performing system checks...

System check identified no issues (0 silenced).  
June 12, 2025 – 18:29:59  
Django version 5.2.3, using settings 'soft_desk_support.settings'  
Starting development server at http://127.0.0.1:8000/  
Quit the server with CONTROL‑C.

WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead.  
For more information on production servers see: https://docs.djangoproject.com/en/5.2/howto/deployment/
```

…then everything’s working fine.

## 5 – How the API Works

First, you need to obtain a **token** to access any data.

Two options:

### 1. Sign up on the Soft Desk platform

Customise the following profile:

```json
{
  "username": "<YOUR_USERNAME>",
  "password": "<YOUR_PASSWORD>",
  "age": 25,
  // 15 is the minimum age required by the app
  "can_be_contacted": false,
  // Set to false if you do NOT want to be contacted
  "can_data_be_shared": false
  // Same if you do NOT want your data shared with third‑party companies
}
```

Then send it to the API.

Via **cURL**:

```bash
curl -X POST "http://127.0.0.1:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "age": 15,
    "can_be_contacted": true,
    "can_data_be_shared": true
  }'
```

…or with **Postman**, for example.

Just drop the JSON in the body of a **POST** request to `http://127.0.0.1:8000/api/users/`.

### 2 – Use this generic profile

```json
{
  "username": "user_6",
  "password": "azer"
}
```

Send this JSON (or your own credentials) in the body of a **POST** request to `http://127.0.0.1:8000/api/token/`.

The response will include your `access` token. Copy it (and keep it somewhere safe) and add it to the headers of any future API requests under the `Authorization` key.

In **Postman**, check the **Bearer Token** option.
Otherwise juste add "Bearer " before the token.

Example:

```http
Authorization: Bearer <YOUR_TOKEN>
```

## 6 – Resources

### — USERS —

You can list every registered user:

|        ENDPOINT       |                 GET                |        POST       |             PUT/PATCH             |        DELETE        |
| :-------------------: | :--------------------------------: | :---------------: | :-------------------------------: | :------------------: |
|      `api/users/`     |      List all registered users     | Create a new user |         `405 NOT ALLOWED`         |   `405 NOT ALLOWED`  |
| `api/users/<int:id>/` | Details for a user (self or admin) | `405 NOT ALLOWED` | Edit some or all fields of a user | Delete own account\* |

\*Deletion is only possible by the user themself or an admin.

**Useful filters**

| Filter                       | Description                       |
| :--------------------------- | :-------------------------------- |
| `?username=<USERNAME>`       | Fetch a user by username          |
| `?id=<USER_ID>`              | Fetch a user by ID                |
| `?contact_ok=true/false`     | Filter by consent to be contacted |
| `?data_shared_ok=true/false` | Filter by consent to share data   |

---

### — PROJECTS —

|             ENDPOINT             |                  GET                 |         POST         |            PUT/PATCH            |         DELETE        |
| :------------------------------: | :----------------------------------: | :------------------: | :-----------------------------: | :-------------------: |
|          `api/projects/`         |      List projects you belong to     | Create a new project |        `405 NOT ALLOWED`        |   `405 NOT ALLOWED`   |
| `api/projects/<int:project_id>/` | Project details (author, type, etc.) |   `405 NOT ALLOWED`  | Edit some or all project fields | Delete (author/admin) |

| Filter             | Description                       |
| :----------------- | :-------------------------------- |
| `name`             | Filter by project name            |
| `author__username` | Filter by project author username |
| `type`             | Filter by project type            |
| `id`               | Filter by project ID              |

*Only contributors can hit these endpoints.*

### — CONTRIBUTORS —

|                    ENDPOINT                    |             GET             |         POST        |                   PUT/PATCH                  |         DELETE         |
| :--------------------------------------------: | :-------------------------: | :-----------------: | :------------------------------------------: | :--------------------: |
|    `api/projects/{project_id}/contributors/`   |     List project members    | Add a contributor\* |               `405 NOT ALLOWED`              |    `405 NOT ALLOWED`   |
| `api/projects/{project_id}/contributors/{id}/` | Contribution details (user) |  `405 NOT ALLOWED`  | Edit some or all contributor‑relation fields | Remove a contributor\* |

A few useful filters :  
  
| Filter      | Description                          |
| :---------- | :----------------------------------- |
| `is_author` | Filter by author status (true/false) |
| `username`  | Filter by username                   |
| `id`        | Filter by contributor ID             |

*Only the project author can add or remove a contributor.*
  

### — ISSUES —

|                    ENDPOINT                    |                   GET                  |        POST       |           PUT/PATCH           |       DELETE      |
| :--------------------------------------------: | :------------------------------------: | :---------------: | :---------------------------: | :---------------: |
|       `api/projects/{project_id}/issues/`      |         List issues (paginated)        | Create an issue\* |       `405 NOT ALLOWED`       | `405 NOT ALLOWED` |
| `api/projects/{project_id}/issues/{issue_id}/` | Issue details (status, assignee, etc.) | `405 NOT ALLOWED` | Edit some or all issue fields | Delete an issue\* |

**Some handy filters**

| Filter        | Description                             |
| :------------ | :-------------------------------------- |
| `priority`    | Issue priority                          |
| `label`       | Associated label                        |
| `status`      | Issue status                            |
| `assignee_id` | Assignee ID                             |
| `is_finished` | Indicates whether the issue is finished |
| `to_do`       | Indicates a to‑do issue                 |

*All contributors can create and view; only authors can edit/delete an issue.*

### — COMMENTS —

|                               ENDPOINT                               |       GET       |        POST       |            PUT/PATCH            |       DELETE       |
| :------------------------------------------------------------------: | :-------------: | :---------------: | :-----------------------------: | :----------------: |
|        `api/projects/{project_id}/issues/{issue_id}/comments/`       |  List comments  |  Add a comment\*  |        `405 NOT ALLOWED`        |  `405 NOT ALLOWED` |
| `api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/` | Comment details | `405 NOT ALLOWED` | Edit some or all comment fields | Delete a comment\* |

*All contributors can comment; only comment authors can delete their own comments.*

## 7 – Pagination

All list endpoints (projects, issues, comments) are paginated by default (5 items per page).
You can tweak this via the params `?limit=<n>&offset=<m>`.

---

# <div align="center"> 🇫🇷 Soft Desk Support 🖇️

## <div align="center"> API REST

Soft Desk Support est une API REST de suivi de projet (gestion de tickets) conçue pour aider les équipes à gérer le développement logiciel. Les utilisateurs peuvent créer un compte puis des projets, ajouter d’autres membres en tant que contributeurs, signaler des problèmes (tickets) au sein de chaque projet, et échanger des solutions via des commentaires. L’application tourne avec **Python 3.11+** et s’appuie sur Django REST Framework.

Tous les endpoints sont sécurisés par des **tokens JWT** – hormis l’inscription et la connexion, un token valide doit être fourni dans les en-têtes de requête. Des règles de permission strictes garantissent que seuls les contributeurs d’un projet peuvent accéder aux données de ce projet, et que seul l’auteur d’une ressource (ou un administrateur) peut la modifier ou la supprimer. Le design suit les recommandations du RGPD : les utilisateurs doivent avoir au moins 15 ans pour s’inscrire, et peuvent choisir s’ils acceptent d’être contactés ou de partager leurs données. Chaque utilisateur dispose également d’un droit d’accès, de rectification et d’effacement de ses données (droit à l’oubli) via son compte. Enfin, dans une démarche de *green code*, toutes les listes sont paginées par défaut (5 éléments par page) afin de minimiser la charge inutile sur le serveur.

## 1 - Clôner le Repo

Copiez/collez la commande suivante dans votre terminal :
*(Pour clôner le projet et se placer à la racine)*

```bash
git clone https://github.com/dim-gggl/softdesk_support.git  
cd softdesk_support
```

## 2 - Environnement virtuel et Dépendances

Le projet a été initialisé avec `poetry` et l’environnement ainsi que les dépendances nécessaires peuvent donc être installés facilement avec la commande :

```bash
poetry install
```

Puis, en fonction de la version de `poetry` dont vous disposez :

```bash
poetry shell
```

> **Attention** – cette commande est dépréciée, préférez :

```bash
eval $(poetry env activate)
```

Si vous n’avez pas `poetry`, vous pouvez tout de même créer un environnement virtuel et installer les dépendances via le fichier `requirements.txt` :

```bash
python3 -m venv .venv  
source .venv/bin/activate  
pip install --upgrade pip  
pip install -r requirements.txt
```

---

## 3 - Variable d’environnement

La SECRET_KEY de Django est déjà chargée automatiquement dès que l'environnement est activé. Si ce n'était pas le cas, vous pouvez suivre les instructions ci-dessous :

Pour éviter de hardcoder la **secret key** de Django, celle-ci a été placée dans le fichier `.env` à la racine du projet. Vous pouvez l’afficher facilement afin de la copier à l’aide de la commande suivante :

```bash
cat .env
```

Copiez la clé, puis exportez-la :

```bash
export DJANGO_SECRET_KEY=<VOTRE_SECRET_KEY>
```

## 4 - Lancement du serveur

Tout est prêt – il ne reste qu’à tester l’API.

```bash
python3 src/manage.py runserver
```

Si votre terminal affiche :

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

…c’est que tout fonctionne.

## 5 - Fonctionnement de l’API

Dans un premier temps, il faut récupérer un **token** afin d’avoir accès aux données.

Pour cela, deux options :

### 1. Vous inscrire sur la plateforme Soft Desk

Personnalisez le profil suivant :

```json
{
  "username": "<VOTRE_PSEUDO>",
  "password": "<VOTRE_MOT_DE_PASSE>",
  "age": 15, 
  // 15 ans est l'âge minimum requis pour l'app
  "can_be_contacted": false, 
  // Mettez false si vous ne souhaitez pas être contacté(e)
  "can_data_be_shared": false 
  // Idem si vous ne souhaitez pas que vos données soient partagées avec des partenaires
}
```

…et envoyez-le à l’API.

Via cURL :

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

…ou via **Postman**, par exemple.

Il suffit d’inclure ce JSON dans le corps de la requête **POST** vers `http://127.0.0.1:8000/api/users/`.

### 2 - Utiliser ce profil générique

```json
{
  "username": "user_6",
  "password": "azer"
}
```

Envoyez ce JSON (ou vos propres identifiants) dans le corps d’une requête **POST** à l’adresse `http://127.0.0.1:8000/api/token/`.

La réponse contiendra votre token (`access`). Copiez-le (et conservez-le précieusement), puis ajoutez-le dans les en-têtes de vos futures requêtes API sous la clé `Authorization`.

Exemple :

```http
Authorization: Bearer <VOTRE_TOKEN>
```

## 6 - Les Ressources

### -- USERS (Utilisateurs) --

Il est possible d’afficher la liste de tous les utilisateurs inscrits :

| ENDPOINT              | GET                                          | POST                       | PUT/PATCH                                         | DELETE                |
| :-------------------- | :------------------------------------------- | :------------------------- | :------------------------------------------------ | :-------------------- |
| `api/users/`          | Liste de tous les utilisateurs inscrits      | Crée un nouvel utilisateur | `405 NOT ALLOWED`                                 | `405 NOT ALLOWED`     |
| `api/users/<int:id>/` | Détails d’un utilisateur (soi-même ou admin) | `405 NOT ALLOWED`          | Modifie tout ou partie des infos d’un utilisateur | Supprime son compte\* |

\*Suppression possible uniquement par l’utilisateur lui-même ou un administrateur.

#### Filtres utiles

| Filtre                       | Description                                          |
| :--------------------------- | :--------------------------------------------------- |
| `?username=<USERNAME>`       | Récupérer un utilisateur par son pseudo              |
| `?id=<USER_ID>`              | Récupérer un utilisateur par son ID                  |
| `?contact_ok=true/false`     | Filtrer selon le consentement à être contacté        |
| `?data_shared_ok=true/false` | Filtrer selon le consentement au partage des données |

---

### -- PROJECTS (Projets) --

| ENDPOINT                         | GET                                     | POST                   | PUT/PATCH                                    | DELETE                  |
| :------------------------------- | :-------------------------------------- | :--------------------- | :------------------------------------------- | :---------------------- |
| `api/projects/`                  | Liste des projets dont vous êtes membre | Crée un nouveau projet | `405 NOT ALLOWED`                            | `405 NOT ALLOWED`       |
| `api/projects/<int:project_id>/` | Détails du projet (auteur, type, etc.)  | `405 NOT ALLOWED`      | Modifie tout ou partie des infos d’un projet | Supprime (auteur/admin) |

| Filtre             | Description                              |
| :----------------- | :--------------------------------------- |
| `name`             | Filtrer par nom du projet                |
| `author__username` | Filtrer par pseudo de l’auteur du projet |
| `type`             | Filtrer par type de projet               |
| `id`               | Filtrer par identifiant du projet        |

*Seuls les contributeurs peuvent accéder à ces endpoints.*

### -- CONTRIBUTORS (Contributeurs) --

| ENDPOINT                                       | GET                                      | POST                     | PUT/PATCH                                                       | DELETE                   |
| :--------------------------------------------- | :--------------------------------------- | :----------------------- | :-------------------------------------------------------------- | :----------------------- |
| `api/projects/{project_id}/contributors/`      | Liste des membres du projet              | Ajoute un contributeur\* | `405 NOT ALLOWED`                                               | `405 NOT ALLOWED`        |
| `api/projects/{project_id}/contributors/{id}/` | Détails d’une contribution (utilisateur) | `405 NOT ALLOWED`        | Modifie tout ou partie des infos d’une relation de contribution | Retire un contributeur\* |

| Filtre      | Description                              |
| :---------- | :--------------------------------------- |
| `is_author` | Filtrer par statut d’auteur (True/False) |
| `username`  | Filtrer par nom d’utilisateur            |
| `id`        | Filtrer par identifiant du contributeur  |

*Seul l’auteur du projet peut ajouter ou retirer un contributeur.*

### -- ISSUES (Tickets) --

| ENDPOINT                                       | GET                                       | POST              | PUT/PATCH                                    | DELETE               |
| :--------------------------------------------- | :---------------------------------------- | :---------------- | :------------------------------------------- | :------------------- |
| `api/projects/{project_id}/issues/`            | Liste des tickets (pagination incluse)    | Crée un ticket\*  | `405 NOT ALLOWED`                            | `405 NOT ALLOWED`    |
| `api/projects/{project_id}/issues/{issue_id}/` | Détails du ticket (statut, assigné, etc.) | `405 NOT ALLOWED` | Modifie tout ou partie des infos d’un ticket | Supprime un ticket\* |

**Quelques filtres utiles**

| Filtre        | Description                          |
| :------------ | :----------------------------------- |
| `priority`    | Priorité du ticket                   |
| `label`       | Étiquette associée                   |
| `status`      | Statut du ticket                     |
| `assignee_id` | Identifiant de l’utilisateur assigné |
| `is_finished` | Indique si le ticket est terminé     |
| `to_do`       | Indique si le ticket est à faire     |
| `urgent`      | Indique si le ticket est urgent      |

*Tous les contributeurs peuvent créer et consulter des tickets ; seuls les auteurs peuvent modifier ou supprimer un ticket.*

### -- COMMENTS (Commentaires) --

| ENDPOINT                                                             | GET                      | POST                    | PUT/PATCH                                         | DELETE                    |
| :------------------------------------------------------------------- | :----------------------- | :---------------------- | :------------------------------------------------ | :------------------------ |
| `api/projects/{project_id}/issues/{issue_id}/comments/`              | Liste des commentaires   | Ajoute un commentaire\* | `405 NOT ALLOWED`                                 | `405 NOT ALLOWED`         |
| `api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/` | Détails d’un commentaire | `405 NOT ALLOWED`       | Modifie tout ou partie des infos d’un commentaire | Supprime un commentaire\* |

*Tous les contributeurs peuvent commenter ; seuls les auteurs d’un commentaire peuvent le supprimer.*

## 7 - Pagination

Toutes les listes (projets, tickets, commentaires) sont paginées par défaut (5 éléments par page).
Vous pouvez ajuster ce comportement via les paramètres `?limit=<n>&offset=<m>`.
