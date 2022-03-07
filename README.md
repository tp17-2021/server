# Server

Voting server public API implemented in FastAPI used to accept incoming votes from the gateway, import data before voting a provide real-time statistics and evaluation after the end of voting.


## How to run it
To start the server container, you need to have Docker installed.

Then navigate to the server root folder of the repository and run
```
docker compose up -d --build
```

After the build, you have two running services (MongoDB database and FastAPI server)

To see all available endpoints of the server navigate to: ```http://localhost:8222/docs```

## Testing inside docker
Unit test implemented inside repository can be run by building the containers, opening CLI in the server container, and running the following command in the code directory:

Docker-compose file for testing purpouse is available. Unit/integration tests can be run inside Docker containers. This is the magic:
```
docker-compose -p test-server -f docker-compose.test.yml up --build --exit-code-from server --renew-anon-volumes 
```

Flags description:
-p                  - preped prefix to container names
-f                  - docker-compose yml file
--build             - build images if changed sources
--exit-code-from    - get overall exit code from specified container
--force-recreate    - recreate all containers
--renew-anon-volumes - delete anonym volumens

_The output of this command is quite... confusing. Output of every container is combined, so not only test results are visible, but also log junk from database. At least, every line prefixes with container name, so grep on Linux can filter it. Although, ignoring otuput from unrelevant containers still remains to be solved smartly._

To stop the contaienrs use command:
```
docker-compose -f docker-compose.test.yml down
```
## API markdown generation

We have created a way to convert open API swagger docs to the readme file and merge it with the original README file to provide all important info about endpoints and their schemas using [widdershins](https://mermade.github.io/widdershins/ConvertingFilesBasicCLI.html) library.

To use it, you need to have a globally installed widdershins node.js library. You can install it using the following command:
```
npm install -g widdershins
```

Afterward .md file can be generated using the command line:
```
widdershins openapi.json -e settings.json -o api_docs.md
```

You do not have to prepare all the necessary files for this command, we have prepared a short python script that downloads the needed files and outputs the resulting new_README.md in its folder. The only thing that needs to be done is to copy to contents and check their correctness.

To run this script please navigate into directory api_docs_2_md and run the following command:
```
python apidoc_2_md.py
```

(Optional)
We use markdown preview VS Code extension [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced) to check the generated .md file before commiting it (shorcut to preview md: ctrl + shift + v).

## API endpoints
---
title: FastAPI v0.1.0
language_tabs:
  - python: Python
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 2

---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="fastapi">FastAPI v0.1.0</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

<h1 id="fastapi-elections">Elections</h1>

## vote_elections_vote_post

<a id="opIdvote_elections_vote_post"></a>

> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/elections/vote', headers = headers)

print(r.json())

```

`POST /elections/vote`

*Vote*

Process candidate's vote

> Body parameter

```json
{
  "votes": [
    {
      "token": "token1",
      "candidates": [
        {
          "candidate_id": "candidate_id1"
        },
        {
          "candidate_id": "candidate_id2"
        }
      ],
      "party_id": "party_id1",
      "election_id": "election_id1",
      "office_id": "office_id1"
    },
    {
      "token": "token2",
      "candidates": [
        {
          "candidate_id": "candidate_id1"
        },
        {
          "candidate_id": "candidate_id2"
        }
      ],
      "party_id": "party_id1",
      "election_id": "election_id1",
      "office_id": "office_id1"
    }
  ],
  "office_id": "office_id1"
}
```

<h3 id="vote_elections_vote_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Votes](#schemaVotes)|true|none|

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string",
  "votes": [],
  "office_id": "string"
}
```

<h3 id="vote_elections_vote_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ResponseServerVoteSchema](#schemaresponseservervoteschema)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## vote_seeder_elections_seed_votes__number__get

<a id="opIdvote_seeder_elections_seed_votes__number__get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/elections/seed/votes/{number}', headers = headers)

print(r.json())

```

`GET /elections/seed/votes/{number}`

*Vote Seeder*

Immitate voting process

<h3 id="vote_seeder_elections_seed_votes__number__get-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|number|path|integer|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="vote_seeder_elections_seed_votes__number__get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="vote_seeder_elections_seed_votes__number__get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## elections_voting_data_elections_voting_data_get

<a id="opIdelections_voting_data_elections_voting_data_get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/elections/voting-data', headers = headers)

print(r.json())

```

`GET /elections/voting-data`

*Elections Voting Data*

> Example responses

> 200 Response

```json
null
```

<h3 id="elections_voting_data_elections_voting_data_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="elections_voting_data_elections_voting_data_get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="fastapi-statistics">Statistics</h1>

## statistics_live_statistics_live_get

<a id="opIdstatistics_live_statistics_live_get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/statistics/live', headers = headers)

print(r.json())

```

`GET /statistics/live`

*Statistics Live*

> Example responses

> 200 Response

```json
null
```

<h3 id="statistics_live_statistics_live_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="statistics_live_statistics_live_get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## statistics_final_statistics_final_get

<a id="opIdstatistics_final_statistics_final_get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/statistics/final', headers = headers)

print(r.json())

```

`GET /statistics/final`

*Statistics Final*

> Example responses

> 200 Response

```json
null
```

<h3 id="statistics_final_statistics_final_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="statistics_final_statistics_final_get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="fastapi-database">Database</h1>

## db_schema_database_schema_get

<a id="opIddb_schema_database_schema_get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/database/schema', headers = headers)

print(r.json())

```

`GET /database/schema`

*Db Schema*

Get all collections from database

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string",
  "collections": []
}
```

<h3 id="db_schema_database_schema_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ResponseDatabaseSchema](#schemaresponsedatabaseschema)|

<aside class="success">
This operation does not require authentication
</aside>

## import_polling_places_database_import_polling_places_post

<a id="opIdimport_polling_places_database_import_polling_places_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/database/import-polling-places', headers = headers)

print(r.json())

```

`POST /database/import-polling-places`

*Import Polling Places*

> Example responses

> 200 Response

```json
null
```

<h3 id="import_polling_places_database_import_polling_places_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="import_polling_places_database_import_polling_places_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## create_key_paris_for_polling_places_database_create_key_pairs_post

<a id="opIdcreate_key_paris_for_polling_places_database_create_key_pairs_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/database/create-key-pairs', headers = headers)

print(r.json())

```

`POST /database/create-key-pairs`

*Create Key Paris For Polling Places*

> Example responses

> 200 Response

```json
null
```

<h3 id="create_key_paris_for_polling_places_database_create_key_pairs_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="create_key_paris_for_polling_places_database_create_key_pairs_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## test_encryption_decryption_database_test_encryption_decryption_post

<a id="opIdtest_encryption_decryption_database_test_encryption_decryption_post"></a>

> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/database/test-encryption-decryption', headers = headers)

print(r.json())

```

`POST /database/test-encryption-decryption`

*Test Encryption Decryption*

> Body parameter

```json
{
  "some text field": "Hi there!",
  "some number": 123,
  "some list": [],
  "some dict": {}
}
```

<h3 id="test_encryption_decryption_database_test_encryption_decryption_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[RequestEncryptionDecryptionTestSchema](#schemarequestencryptiondecryptiontestschema)|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="test_encryption_decryption_database_test_encryption_decryption_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="test_encryption_decryption_database_test_encryption_decryption_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## import_data_database_import_data_post

<a id="opIdimport_data_database_import_data_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/database/import-data', headers = headers)

print(r.json())

```

`POST /database/import-data`

*Import Data*

> Example responses

> 200 Response

```json
null
```

<h3 id="import_data_database_import_data_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="import_data_database_import_data_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="fastapi-root">Root</h1>

## root__get

<a id="opIdroot__get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/', headers = headers)

print(r.json())

```

`GET /`

*Root*

> Example responses

> 200 Response

```json
null
```

<h3 id="root__get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="root__get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

# Schemas

<h2 id="tocS_Collection">Collection</h2>
<!-- backwards compatibility -->
<a id="schemacollection"></a>
<a id="schema_Collection"></a>
<a id="tocScollection"></a>
<a id="tocscollection"></a>

```json
{
  "name": "string",
  "keys": []
}

```

Collection

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|keys|[string]|false|none|none|

<h2 id="tocS_HTTPValidationError">HTTPValidationError</h2>
<!-- backwards compatibility -->
<a id="schemahttpvalidationerror"></a>
<a id="schema_HTTPValidationError"></a>
<a id="tocShttpvalidationerror"></a>
<a id="tocshttpvalidationerror"></a>

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|none|

<h2 id="tocS_RequestEncryptionDecryptionTestSchema">RequestEncryptionDecryptionTestSchema</h2>
<!-- backwards compatibility -->
<a id="schemarequestencryptiondecryptiontestschema"></a>
<a id="schema_RequestEncryptionDecryptionTestSchema"></a>
<a id="tocSrequestencryptiondecryptiontestschema"></a>
<a id="tocsrequestencryptiondecryptiontestschema"></a>

```json
{
  "some text field": "Hi there!",
  "some number": 123,
  "some list": [],
  "some dict": {}
}

```

RequestEncryptionDecryptionTestSchema

### Properties

*None*

<h2 id="tocS_Votes">Votes</h2>
<!-- backwards compatibility -->
<a id="schemaVotes"></a>
<a id="schema_Votes"></a>
<a id="tocSVotes"></a>
<a id="tocsVotes"></a>

```json
{
  "votes": [
    {
      "token": "token1",
      "candidates": [
        {
          "candidate_id": "candidate_id1"
        },
        {
          "candidate_id": "candidate_id2"
        }
      ],
      "party_id": "party_id1",
      "election_id": "election_id1",
      "office_id": "office_id1"
    },
    {
      "token": "token2",
      "candidates": [
        {
          "candidate_id": "candidate_id1"
        },
        {
          "candidate_id": "candidate_id2"
        }
      ],
      "party_id": "party_id1",
      "election_id": "election_id1",
      "office_id": "office_id1"
    }
  ],
  "office_id": "office_id1"
}

```

Votes

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|votes|[[Vote](#schemaservervote)]|true|none|none|
|office_id|string|true|none|none|

<h2 id="tocS_ResponseDatabaseSchema">ResponseDatabaseSchema</h2>
<!-- backwards compatibility -->
<a id="schemaresponsedatabaseschema"></a>
<a id="schema_ResponseDatabaseSchema"></a>
<a id="tocSresponsedatabaseschema"></a>
<a id="tocsresponsedatabaseschema"></a>

```json
{
  "status": "string",
  "message": "string",
  "collections": []
}

```

ResponseDatabaseSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status|string|true|none|none|
|message|string|true|none|none|
|collections|[[Collection](#schemacollection)]|false|none|none|

<h2 id="tocS_ResponseServerVoteSchema">ResponseServerVoteSchema</h2>
<!-- backwards compatibility -->
<a id="schemaresponseservervoteschema"></a>
<a id="schema_ResponseServerVoteSchema"></a>
<a id="tocSresponseservervoteschema"></a>
<a id="tocsresponseservervoteschema"></a>

```json
{
  "status": "string",
  "message": "string",
  "votes": [],
  "office_id": "string"
}

```

ResponseServerVoteSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status|string|true|none|none|
|message|string|true|none|none|
|votes|[[Vote](#schemaservervote)]|false|none|none|
|office_id|string|true|none|none|

<h2 id="tocS_ServerCandidate">Candidate</h2>
<!-- backwards compatibility -->
<a id="schemaservercandidate"></a>
<a id="schema_ServerCandidate"></a>
<a id="tocSservercandidate"></a>
<a id="tocsservercandidate"></a>

```json
{
  "candidate_id": "string"
}

```

Candidate

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|candidate_id|string|true|none|none|

<h2 id="tocS_ServerVote">Vote</h2>
<!-- backwards compatibility -->
<a id="schemaservervote"></a>
<a id="schema_ServerVote"></a>
<a id="tocSservervote"></a>
<a id="tocsservervote"></a>

```json
{
  "token": "token1",
  "candidates": [
    {
      "candidate_id": "candidate_id1"
    },
    {
      "candidate_id": "candidate_id2"
    }
  ],
  "party_id": "party_id1",
  "election_id": "election_id1",
  "office_id": "office_id1"
}

```

Vote

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|token|string|true|none|none|
|candidates|[[Candidate](#schemaservercandidate)]|false|none|none|
|party_id|string|true|none|none|
|election_id|string|true|none|none|
|office_id|string|true|none|none|

<h2 id="tocS_ValidationError">ValidationError</h2>
<!-- backwards compatibility -->
<a id="schemavalidationerror"></a>
<a id="schema_ValidationError"></a>
<a id="tocSvalidationerror"></a>
<a id="tocsvalidationerror"></a>

```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|loc|[string]|true|none|none|
|msg|string|true|none|none|
|type|string|true|none|none|

