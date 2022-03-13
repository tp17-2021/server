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

<h1 id="fastapi-database">Database</h1>

## schema_database_schema_get

<a id="opIdschema_database_schema_get"></a>

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

*Schema*

Get all collections from database

> Example responses

> 200 Response

```json
{
  "collections": []
}
```

<h3 id="schema_database_schema_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Collections](#schemacollections)|

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
{
  "status": "string",
  "message": "string"
}
```

<h3 id="import_data_database_import_data_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Message](#schemamessage)|

<aside class="success">
This operation does not require authentication
</aside>

## seed_data_database_seed_data_post

<a id="opIdseed_data_database_seed_data_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/database/seed-data', params={
  'number_of_votes': '0'
}, headers = headers)

print(r.json())

```

`POST /database/seed-data`

*Seed Data*

<h3 id="seed_data_database_seed_data_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|number_of_votes|query|integer|true|none|

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string"
}
```

<h3 id="seed_data_database_seed_data_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Message](#schemamessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## seed_votes_database_seed_votes_post

<a id="opIdseed_votes_database_seed_votes_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/database/seed-votes', params={
  'number_of_votes': '0'
}, headers = headers)

print(r.json())

```

`POST /database/seed-votes`

*Seed Votes*

<h3 id="seed_votes_database_seed_votes_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|number_of_votes|query|integer|true|none|

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string"
}
```

<h3 id="seed_votes_database_seed_votes_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Message](#schemamessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

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
  "polling_place_id": 0,
  "votes": [
    {
      "encrypted_message": "36AMNvcpAWdHAXKCSWexgyjxrt7xeWwhOf+oUMBqip/C051EZWlN4N4x3hVPwwIQh/l78suUNYYYQBTkERPkuaZ40D1NV4LM7nb+DHcQ0nzGIFxHND3CIDkT9UOi1AmrqrCtyVMpDP1SI/2glHjbMsrw9VowA3L8hbf3U4wSF65ocF5IxN8mrOraXUopMcu+GgFKjBh3Y56yhZfxwr7go2YvQwph1HuLYVkkBi3ZAk+1DHCuQ+oQC3ivVJPF6SBOHPJIgLGM5NUsJwq5MUWSgxlr+iQI/g/uWbjkcS7M9uBZE6+QRTD++6sqZhHxc8RTLVtqAmrp0m1We6kf/Nrx7KdqagpHQz1vgZEf50L+kVgXf9PnX1THB7U+jVB0ogvM1fmZ+JvWURHt9ZhgdO1wZvzigQP6jTNZw5amzga2T+6/KwC47dxdnnT/l/fSBXzgAbsCNWCegJfTakvpsCNjWRlPKIvbPcGEIZDKBaMTz/zhKHqTgQV/f3qmlHgq+GYVPsyl95NVBFiiYwWxYWvJIl8RCREfx39t2bAx74YsJ4fT8G3u438l6BvT5DMrEbN3YlAS7gwuRt4j3AQUWmyzHesIW1o/pJd+5IpNYQ3ld6363iu5G4mC00lnImnSig==",
      "encrypted_object": "lb5B/LAg2/38mot9jYzRpa9O6YwrXDilpspPrGrnTKKYUXVfQ9JhW5JIGoP6FuQBXM2XzlcXkb90/VDK6+h/HeJKEUf81h/A/KiN4AZVBtRoHXOpq1gyRpFk7q5dhHzniStAPZOLruNtrAYmOoUNq3hmHLxs2KnRTMZiEc9kOefIS1vjPKFAClNCqKL++7orwvRPWGzmLMPbq6DFc/Sb7hXVlBMiUCmS2iMtz9mgs9IXheCqvcGYZQZOubFK3zjtqOvFEjuGACUZkuGbmxHEFgbBMCUPXOH933aP8eNY33+UIKSc2DSNKTOOySJNi3EolJmUhbQT5NIWXf9lE3jqXg=="
    }
  ]
}
```

<h3 id="vote_elections_vote_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[VotesEncrypted](#schemavotesencrypted)|true|none|

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string"
}
```

<h3 id="vote_elections_vote_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Message](#schemamessage)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## get_voting_data_elections_voting_data_get

<a id="opIdget_voting_data_elections_voting_data_get"></a>

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

*Get Voting Data*

Downlaod voting data json using command curl http://localhost:8222/elections/voting-data > config.json

> Example responses

> 200 Response

```json
{
  "polling_places": [],
  "parties": [],
  "key_pairs": [],
  "texts": {
    "elections_name_short": {
      "sk": "string",
      "en": "string"
    },
    "elections_name_long": {
      "sk": "string",
      "en": "string"
    },
    "election_date": {
      "sk": "string",
      "en": "string"
    }
  }
}
```

<h3 id="get_voting_data_elections_voting_data_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[VotingData](#schemavotingdata)|

<aside class="success">
This operation does not require authentication
</aside>

## get_zapisnica_elections_zapisnica_get

<a id="opIdget_zapisnica_elections_zapisnica_get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/elections/zapisnica', headers = headers)

print(r.json())

```

`GET /elections/zapisnica`

*Get Zapisnica*

> Example responses

> 200 Response

```json
null
```

<h3 id="get_zapisnica_elections_zapisnica_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="get_zapisnica_elections_zapisnica_get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="fastapi-elastic-search">Elastic search</h1>

## setup_elastic_votes_index_elastic_setup_elastic_vote_index_post

<a id="opIdsetup_elastic_votes_index_elastic_setup_elastic_vote_index_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/elastic/setup-elastic-vote-index', headers = headers)

print(r.json())

```

`POST /elastic/setup-elastic-vote-index`

*Setup Elastic Votes Index*

Setup elastic search. Drop index if previously used. Create new index and variables mapping.

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string"
}
```

<h3 id="setup_elastic_votes_index_elastic_setup_elastic_vote_index_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Message](#schemamessage)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Internal Server Error|[Message](#schemamessage)|

<aside class="success">
This operation does not require authentication
</aside>

## synchronize_votes_ES_elastic_synchronize_votes_es_post

<a id="opIdsynchronize_votes_ES_elastic_synchronize_votes_es_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/elastic/synchronize-votes-es', headers = headers)

print(r.json())

```

`POST /elastic/synchronize-votes-es`

*Synchronize Votes Es*

Batch synchronization of votes from Mongo DB to Elastic search 3 Node cluster. Shuld be called in specific intervals during election period.

<h3 id="synchronize_votes_es_elastic_synchronize_votes_es_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|number|query|any|false|none|

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string"
}
```

<h3 id="synchronize_votes_es_elastic_synchronize_votes_es_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Message](#schemamessage)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Internal Server Error|[Message](#schemamessage)|

<aside class="success">
This operation does not require authentication
</aside>

## get_parties_results_elastic_get_parties_results_post

<a id="opIdget_parties_results_elastic_get_parties_results_post"></a>

> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/elastic/get-parties-results', headers = headers)

print(r.json())

```

`POST /elastic/get-parties-results`

*Get Parties Results*

> Body parameter

```json
{
  "party": "SME RODINA"
}
```

<h3 id="get_parties_results_elastic_get_parties_results_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[StatisticsPerPartyRequest](#schemastatisticsperpartyrequest)|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="get_parties_results_elastic_get_parties_results_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Internal Server Error|[Message](#schemamessage)|

<h3 id="get_parties_results_elastic_get_parties_results_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## get_parties_with_candidates_results_elastic_get_party_candidate_results_post

<a id="opIdget_parties_with_candidates_results_elastic_get_party_candidate_results_post"></a>

> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/elastic/get-party-candidate-results', headers = headers)

print(r.json())

```

`POST /elastic/get-party-candidate-results`

*Get Parties With Candidates Results*

> Body parameter

```json
{
  "party": "SME RODINA"
}
```

<h3 id="get_parties_with_candidates_results_elastic_get_party_candidate_results_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[StatisticsPerPartyRequest](#schemastatisticsperpartyrequest)|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="get_parties_with_candidates_results_elastic_get_party_candidate_results_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Internal Server Error|[Message](#schemamessage)|

<h3 id="get_parties_with_candidates_results_elastic_get_party_candidate_results_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## get_candidates_results_elastic_get_candidates_results_post

<a id="opIdget_candidates_results_elastic_get_candidates_results_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/elastic/get-candidates-results', headers = headers)

print(r.json())

```

`POST /elastic/get-candidates-results`

*Get Candidates Results*

> Example responses

> 200 Response

```json
null
```

<h3 id="get_candidates_results_elastic_get_candidates_results_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Internal Server Error|[Message](#schemamessage)|

<h3 id="get_candidates_results_elastic_get_candidates_results_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## get_resilts_by_locality_mongo_elastic_get_results_by_locality_mongo_get

<a id="opIdget_resilts_by_locality_mongo_elastic_get_results_by_locality_mongo_get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/elastic/get-results-by-locality-mongo', headers = headers)

print(r.json())

```

`GET /elastic/get-results-by-locality-mongo`

*Get Resilts By Locality Mongo*

Used to provide benchmark for ES vs Mongo aggregation queries

> Example responses

> 200 Response

```json
null
```

<h3 id="get_resilts_by_locality_mongo_elastic_get_results_by_locality_mongo_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="get_resilts_by_locality_mongo_elastic_get_results_by_locality_mongo_get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## get_results_by_locality_elastic_get_results_by_locality_post

<a id="opIdget_results_by_locality_elastic_get_results_by_locality_post"></a>

> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/elastic/get-results-by-locality', headers = headers)

print(r.json())

```

`POST /elastic/get-results-by-locality`

*Get Results By Locality*

> Body parameter

```json
{
  "filter_by": "region_name",
  "filter_value": "Prešovský kraj"
}
```

<h3 id="get_results_by_locality_elastic_get_results_by_locality_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[StatisticsPerLocalityRequest](#schemastatisticsperlocalityrequest)|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="get_results_by_locality_elastic_get_results_by_locality_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Internal Server Error|[Message](#schemamessage)|

<h3 id="get_results_by_locality_elastic_get_results_by_locality_post-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## get_elections_status_elastic_elections_status_get

<a id="opIdget_elections_status_elastic_elections_status_get"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/elastic/elections-status', headers = headers)

print(r.json())

```

`GET /elastic/elections-status`

*Get Elections Status*

> Example responses

> 200 Response

```json
null
```

<h3 id="get_elections_status_elastic_elections_status_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad Request|[Message](#schemamessage)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Internal Server Error|[Message](#schemamessage)|

<h3 id="get_elections_status_elastic_elections_status_get-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="fastapi-encryption">Encryption</h1>

## create_key_pairs_for_polling_places_encryption_key_pairs_post

<a id="opIdcreate_key_pairs_for_polling_places_encryption_key_pairs_post"></a>

> Code samples

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.post('/encryption/key-pairs', headers = headers)

print(r.json())

```

`POST /encryption/key-pairs`

*Create Key Pairs For Polling Places*

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string"
}
```

<h3 id="create_key_pairs_for_polling_places_encryption_key_pairs_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Message](#schemamessage)|

<aside class="success">
This operation does not require authentication
</aside>

## test_encrypt_vote_encryption_test_encrypt_vote_post

<a id="opIdtest_encrypt_vote_encryption_test_encrypt_vote_post"></a>

> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/encryption/test-encrypt-vote', headers = headers)

print(r.json())

```

`POST /encryption/test-encrypt-vote`

*Test Encrypt Vote*

> Body parameter

```json
{
  "vote": {
    "token": "fjosjfidsw",
    "party_id": 10,
    "election_id": "election_id",
    "candidate_ids": [
      1158,
      1077,
      1191
    ]
  },
  "g_private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo+2EFBBRiHoDJazdLO+dckpHDpwwQ\nLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF0SsocvKeJ5orgaMeC2kjkgf1gMec\nwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDohqkWpgguAOQnEzt07c2o5drH03km9\nnF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPAYLshpK+awmJ8upqAwy+7JHXPfVz/\nbeShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK0Gxym0UG1LodR9hp+EmWoem8HJqY\nE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AInswIDAQABAoIBAGZLg8WcQIaRNJJt\ngVAKH/BOdpWOobQUYOQ+NoV5eYgl0nzGtVVWoAFcnJ+eGObY2h3+RvxCLoMuA9Kr\n10mlrhVRw2zSsVcsaxwLIU+7yrKdp0NH19dMnQO4MUOO6RhW3feaH/vWTWZtrRA8\nRt4wMYGZHefQVFh9Skr+AQR1YxJqpvNAahOJuAkoK5wkMtOmDQFI9VYPARFH1tSL\nE1Rf9aQ4Y2ZGffZsr9i1adzrX0uAPFpXH5EZVwYx5hr/HPfP3xgiZ9aP4kJjHTwp\n4T1k5KYHN9mH6oQccGi9GNOPGZQagtid/g6IsWIgdiVOWyjoNT8jWBQLa7Kl57n6\n4x25uJECgYEA2xXcj1zxc1wjJpVDN7mOStbrk9ngLZRhU34UVxzCugbMFesBRO9X\n39u7t80D6Q7cJ9JE4LrBTYJd736k5oFp3Hzea4jmD4zPUKSRR8BD5dQ7th/XOcvo\njaEyoWD0kWblTqkAinfoKzt4HxEsBBAsIh0PyhgWz4yoBuI0LZgX44kCgYEA+ZGP\nWbfXm9ZrMWU3Owhdqr3J1YqJKNMa+ydQC2xxnv4LAbiSnKyAGACiAP8ymKceU0bA\nHtQUaLoYeMEJcJ6fSK9xFcrUB+VRxmvcG9zrwoYUjRMxSPoMh+r68vzGCpQ7ZcSQ\noLd67ncWD1X2uPeyqex83N+e++ih5q2IcUwillsCgYB3A89HikQYWQs3YIqdcQ3d\nlhdvwEJKQHsGsk02bYdTK3IezgVof2ULVQEK/jKLnuj2MQH92zY7dwC0o+XM2qy5\nfJQPctUXyXSt6FiL0+SOq9asP2vaF+2DUviANn1lp7IWIzUKA815/tpodhmlM2vm\nNEdpj+CEa3K0Gpoh0qfXkQKBgQCCwOB6APfVjeFbX8wwAZIRgp3cY1i5KuFX9KDb\nW1WsFy1tGWa27ymtaad3Hj1D/UrGFqtRe4u10so/eeOYPYL2cfStljbAbEUL0Dbh\n4j0jDVx3DTclJNyr2VDhPc4EfOUhzHp5uaeOiJXmMwOwpRXWMTC6B+8jzB4G3aQ+\nt8TnQQKBgQDCLjDCEc/l3KHQYfTpxX1EIvoqEJSIRUyXjuICj0kP+fBXcWiYEEd4\njJTryVRmIulyJTuxAhhBNXlHGIMPX2fmU7IGgRKO/2kvb2yLGTnfecUGwPL4YEGy\nw0yCPjyhu9/fpr1lDUJ0NN+GmpqplkqvXtYPLdJSIigDVW7Jn/stRQ==\n-----END RSA PRIVATE KEY-----",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs6lvNfr+Eo6Mt+mW95fh\njUbCRygCNok8Y8yIu502lpDiz3bNdR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7I\nEpRSmY1nElabMoBbU2vsPWBsu7WR31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPu\nRVtuHy/q2tD5sY2ekWJc1YsoeQ5JDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c\n2P4NpNgSJ2NT8aF/bDbu3sQk9QuQXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchq\nrYj5Xnql/wcrnyOhcgeKsOBieH/fETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG4\n7QIDAQAB\n-----END PUBLIC KEY-----"
}
```

<h3 id="test_encrypt_vote_encryption_test_encrypt_vote_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[VoteToBeEncrypted](#schemavotetobeencrypted)|true|none|

> Example responses

> 200 Response

```json
{
  "encrypted_message": "string",
  "encrypted_object": "string"
}
```

<h3 id="test_encrypt_vote_encryption_test_encrypt_vote_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[VoteEncrypted](#schemavoteencrypted)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## test_decrypt_vote_encryption_test_decrypt_vote_post

<a id="opIdtest_decrypt_vote_encryption_test_decrypt_vote_post"></a>

> Code samples

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/encryption/test-decrypt-vote', headers = headers)

print(r.json())

```

`POST /encryption/test-decrypt-vote`

*Test Decrypt Vote*

> Body parameter

```json
{
  "encrypted_vote": {
    "encrypted_message": "ZiwaJl+BScLyGgpGqOu4jSG/MJ4vtgCYm4f6j5xh4TThD49y972z9bWALEe166HZzgKpqsBD36Vbstvd0VL8FeEF8TttOZWrBo1uT6c7d2Z5EzHWPAE5oScYwZ4288s8XJ+dHQv8h9dXpEaxGtKG/mzz3mhNh3oUwZ3T2DvlyUTEeMsD363XVpsyZy47je4mKEWBfEZgoC86OI6pYJ0Ckcxa5X0D7eql5ElzEHfVSpXr1LOh9DLzC+Hrj1oIIcYKSsw0uf275Pk+E1B34kDr+pePgBvRQIwQzXZP5KUPSil5U7qbiNjUy0M9Ztx1FZB0/YUux46AhHQdQhvDQ6gWeSlYV4tCJaKD+KTRqaLMUSZknOJLmWn1Ci1s95NIBlwP6izyhnCLPaiNaKdxmbbYOU6u6eBQ0ZRKS3ibW6s/tqtazfznF3fLdl6sn0KS7Yknkcg8Z3b7QSjrzcOsEhzw62AtblSUma7+mH3PXqDmXyuNjh1SG9ShbYA5CKdOmZZ6ksm8MWkfjtIiifN9bC+vgy7NuqWtdgfbb7CiqCMTm67/p2yG2wQEwsYEMbDc0LAYrfR5qtRxxy5bTdSXZWLXPcueS31tblkkMOW7BIk/dZCGeiSsFZ1wJOataPOlMg==",
    "encrypted_object": "oN59MQBwMNsdeABCNQt/I8DsDYLx3VdaIIGcBn06VhKArg/aTU5uomXkZs0+8Apm3ELYtHmNWeqpTms26PcFcyViEvFaylAja12ic5qs71Fg3LKzbXu1kB7SgBqDGcXQL2iAuaoBuLlrrTm0dJ69spduSekM/PUWWJwh5wTsMHGGoPJd2BgzwO2R+5RTEaeM733+D5/BYMbXlsOFfyfDhD4B8u297/hVAGLtHq666gHGJREsuaj+wzNx7JqB+PBGCjJa0CE519txpaztU9N9QMMuVwn/J6QHUbOTJk/KVDxcmWD6L9wAal00jwEnT7R9XlhOLJx4rdtxqfZ6ZNC7Jw=="
  },
  "private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----",
  "g_public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo\n+2EFBBRiHoDJazdLO+dckpHDpwwQLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF\n0SsocvKeJ5orgaMeC2kjkgf1gMecwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDoh\nqkWpgguAOQnEzt07c2o5drH03km9nF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPA\nYLshpK+awmJ8upqAwy+7JHXPfVz/beShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK\n0Gxym0UG1LodR9hp+EmWoem8HJqYE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AIn\nswIDAQAB\n-----END PUBLIC KEY-----"
}
```

<h3 id="test_decrypt_vote_encryption_test_decrypt_vote_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[VoteToBeDecrypted](#schemavotetobedecrypted)|true|none|

> Example responses

> 200 Response

```json
{
  "token": "string",
  "party_id": 0,
  "election_id": "string",
  "candidate_ids": []
}
```

<h3 id="test_decrypt_vote_encryption_test_decrypt_vote_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[Vote](#schemavote)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

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

<h2 id="tocS_Candidate">Candidate</h2>
<!-- backwards compatibility -->
<a id="schemacandidate"></a>
<a id="schema_Candidate"></a>
<a id="tocScandidate"></a>
<a id="tocscandidate"></a>

```json
{
  "_id": 0,
  "party_number": 0,
  "order": 0,
  "first_name": "string",
  "last_name": "string",
  "degrees_before": "string",
  "age": 0,
  "occupation": "string",
  "residence": "string"
}

```

Candidate

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|_id|integer|true|none|none|
|party_number|integer|true|none|none|
|order|integer|true|none|none|
|first_name|string|true|none|none|
|last_name|string|true|none|none|
|degrees_before|string|true|none|none|
|age|integer|true|none|none|
|occupation|string|true|none|none|
|residence|string|true|none|none|

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

<h2 id="tocS_Collections">Collections</h2>
<!-- backwards compatibility -->
<a id="schemacollections"></a>
<a id="schema_Collections"></a>
<a id="tocScollections"></a>
<a id="tocscollections"></a>

```json
{
  "collections": []
}

```

Collections

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|collections|[[Collection](#schemacollection)]|false|none|none|

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

<h2 id="tocS_KeyPair">KeyPair</h2>
<!-- backwards compatibility -->
<a id="schemakeypair"></a>
<a id="schema_KeyPair"></a>
<a id="tocSkeypair"></a>
<a id="tocskeypair"></a>

```json
{
  "_id": 0,
  "polling_place_id": 0,
  "private_key_pem": "string",
  "public_key_pem": "string",
  "g_private_key_pem": "string",
  "g_public_key_pem": "string"
}

```

KeyPair

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|_id|integer|true|none|none|
|polling_place_id|integer|true|none|none|
|private_key_pem|string|true|none|none|
|public_key_pem|string|true|none|none|
|g_private_key_pem|string|true|none|none|
|g_public_key_pem|string|true|none|none|

<h2 id="tocS_Message">Message</h2>
<!-- backwards compatibility -->
<a id="schemamessage"></a>
<a id="schema_Message"></a>
<a id="tocSmessage"></a>
<a id="tocsmessage"></a>

```json
{
  "status": "string",
  "message": "string"
}

```

Message

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status|string|true|none|none|
|message|string|true|none|none|

<h2 id="tocS_Party">Party</h2>
<!-- backwards compatibility -->
<a id="schemaparty"></a>
<a id="schema_Party"></a>
<a id="tocSparty"></a>
<a id="tocsparty"></a>

```json
{
  "_id": 0,
  "party_number": 0,
  "name": "string",
  "abbreviation": "string",
  "image": "string",
  "image_bytes": "string",
  "color": "string",
  "candidates": []
}

```

Party

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|_id|integer|true|none|none|
|party_number|integer|true|none|none|
|name|string|true|none|none|
|abbreviation|string|true|none|none|
|image|string|true|none|none|
|image_bytes|string|true|none|none|
|color|string|true|none|none|
|candidates|[[Candidate](#schemacandidate)]|false|none|none|

<h2 id="tocS_PollingPlace">PollingPlace</h2>
<!-- backwards compatibility -->
<a id="schemapollingplace"></a>
<a id="schema_PollingPlace"></a>
<a id="tocSpollingplace"></a>
<a id="tocspollingplace"></a>

```json
{
  "region_code": 1,
  "region_name": "Bratislavský kraj",
  "administrative_area_code": 101,
  "administrative_area_name": "Bratislava",
  "county_code": 101,
  "county_name": "Bratislava I",
  "municipality_code": 528595,
  "municipality_name": "Bratislava - Staré Mesto",
  "polling_place_number": 1,
  "registered_voters_count": 1234
}

```

PollingPlace

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|_id|integer|true|none|none|
|region_code|integer|true|none|none|
|region_name|string|true|none|none|
|administrative_area_code|integer|true|none|none|
|administrative_area_name|string|true|none|none|
|county_code|integer|true|none|none|
|county_name|string|true|none|none|
|municipality_code|integer|true|none|none|
|municipality_name|string|true|none|none|
|polling_place_number|integer|true|none|none|
|registered_voters_count|integer|true|none|none|

<h2 id="tocS_StatisticsPerLocalityRequest">StatisticsPerLocalityRequest</h2>
<!-- backwards compatibility -->
<a id="schemastatisticsperlocalityrequest"></a>
<a id="schema_StatisticsPerLocalityRequest"></a>
<a id="tocSstatisticsperlocalityrequest"></a>
<a id="tocsstatisticsperlocalityrequest"></a>

```json
{
  "filter_by": "region_name",
  "filter_value": "Prešovský kraj"
}

```

StatisticsPerLocalityRequest

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|filter_by|string|true|none|none|
|filter_value|string|false|none|none|

<h2 id="tocS_StatisticsPerPartyRequest">StatisticsPerPartyRequest</h2>
<!-- backwards compatibility -->
<a id="schemastatisticsperpartyrequest"></a>
<a id="schema_StatisticsPerPartyRequest"></a>
<a id="tocSstatisticsperpartyrequest"></a>
<a id="tocsstatisticsperpartyrequest"></a>

```json
{
  "party": "SME RODINA"
}

```

StatisticsPerPartyRequest

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|party|string|false|none|none|

<h2 id="tocS_Text">Text</h2>
<!-- backwards compatibility -->
<a id="schematext"></a>
<a id="schema_Text"></a>
<a id="tocStext"></a>
<a id="tocstext"></a>

```json
{
  "sk": "string",
  "en": "string"
}

```

Text

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sk|string|true|none|none|
|en|string|true|none|none|

<h2 id="tocS_Texts">Texts</h2>
<!-- backwards compatibility -->
<a id="schematexts"></a>
<a id="schema_Texts"></a>
<a id="tocStexts"></a>
<a id="tocstexts"></a>

```json
{
  "elections_name_short": {
    "sk": "string",
    "en": "string"
  },
  "elections_name_long": {
    "sk": "string",
    "en": "string"
  },
  "election_date": {
    "sk": "string",
    "en": "string"
  }
}

```

Texts

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|elections_name_short|[Text](#schematext)|true|none|none|
|elections_name_long|[Text](#schematext)|true|none|none|
|election_date|[Text](#schematext)|true|none|none|

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

<h2 id="tocS_Vote">Vote</h2>
<!-- backwards compatibility -->
<a id="schemavote"></a>
<a id="schema_Vote"></a>
<a id="tocSvote"></a>
<a id="tocsvote"></a>

```json
{
  "token": "string",
  "party_id": 0,
  "election_id": "string",
  "candidate_ids": []
}

```

Vote

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|token|string|true|none|none|
|party_id|integer|true|none|none|
|election_id|string|true|none|none|
|candidate_ids|[integer]|false|none|none|

<h2 id="tocS_VoteEncrypted">VoteEncrypted</h2>
<!-- backwards compatibility -->
<a id="schemavoteencrypted"></a>
<a id="schema_VoteEncrypted"></a>
<a id="tocSvoteencrypted"></a>
<a id="tocsvoteencrypted"></a>

```json
{
  "encrypted_message": "string",
  "encrypted_object": "string"
}

```

VoteEncrypted

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|encrypted_message|string|true|none|none|
|encrypted_object|string|true|none|none|

<h2 id="tocS_VoteToBeDecrypted">VoteToBeDecrypted</h2>
<!-- backwards compatibility -->
<a id="schemavotetobedecrypted"></a>
<a id="schema_VoteToBeDecrypted"></a>
<a id="tocSvotetobedecrypted"></a>
<a id="tocsvotetobedecrypted"></a>

```json
{
  "encrypted_vote": {
    "encrypted_message": "ZiwaJl+BScLyGgpGqOu4jSG/MJ4vtgCYm4f6j5xh4TThD49y972z9bWALEe166HZzgKpqsBD36Vbstvd0VL8FeEF8TttOZWrBo1uT6c7d2Z5EzHWPAE5oScYwZ4288s8XJ+dHQv8h9dXpEaxGtKG/mzz3mhNh3oUwZ3T2DvlyUTEeMsD363XVpsyZy47je4mKEWBfEZgoC86OI6pYJ0Ckcxa5X0D7eql5ElzEHfVSpXr1LOh9DLzC+Hrj1oIIcYKSsw0uf275Pk+E1B34kDr+pePgBvRQIwQzXZP5KUPSil5U7qbiNjUy0M9Ztx1FZB0/YUux46AhHQdQhvDQ6gWeSlYV4tCJaKD+KTRqaLMUSZknOJLmWn1Ci1s95NIBlwP6izyhnCLPaiNaKdxmbbYOU6u6eBQ0ZRKS3ibW6s/tqtazfznF3fLdl6sn0KS7Yknkcg8Z3b7QSjrzcOsEhzw62AtblSUma7+mH3PXqDmXyuNjh1SG9ShbYA5CKdOmZZ6ksm8MWkfjtIiifN9bC+vgy7NuqWtdgfbb7CiqCMTm67/p2yG2wQEwsYEMbDc0LAYrfR5qtRxxy5bTdSXZWLXPcueS31tblkkMOW7BIk/dZCGeiSsFZ1wJOataPOlMg==",
    "encrypted_object": "oN59MQBwMNsdeABCNQt/I8DsDYLx3VdaIIGcBn06VhKArg/aTU5uomXkZs0+8Apm3ELYtHmNWeqpTms26PcFcyViEvFaylAja12ic5qs71Fg3LKzbXu1kB7SgBqDGcXQL2iAuaoBuLlrrTm0dJ69spduSekM/PUWWJwh5wTsMHGGoPJd2BgzwO2R+5RTEaeM733+D5/BYMbXlsOFfyfDhD4B8u297/hVAGLtHq666gHGJREsuaj+wzNx7JqB+PBGCjJa0CE519txpaztU9N9QMMuVwn/J6QHUbOTJk/KVDxcmWD6L9wAal00jwEnT7R9XlhOLJx4rdtxqfZ6ZNC7Jw=="
  },
  "private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----",
  "g_public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo\n+2EFBBRiHoDJazdLO+dckpHDpwwQLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF\n0SsocvKeJ5orgaMeC2kjkgf1gMecwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDoh\nqkWpgguAOQnEzt07c2o5drH03km9nF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPA\nYLshpK+awmJ8upqAwy+7JHXPfVz/beShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK\n0Gxym0UG1LodR9hp+EmWoem8HJqYE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AIn\nswIDAQAB\n-----END PUBLIC KEY-----"
}

```

VoteToBeDecrypted

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|encrypted_vote|[VoteEncrypted](#schemavoteencrypted)|true|none|none|
|private_key_pem|string|true|none|none|
|g_public_key_pem|string|true|none|none|

<h2 id="tocS_VoteToBeEncrypted">VoteToBeEncrypted</h2>
<!-- backwards compatibility -->
<a id="schemavotetobeencrypted"></a>
<a id="schema_VoteToBeEncrypted"></a>
<a id="tocSvotetobeencrypted"></a>
<a id="tocsvotetobeencrypted"></a>

```json
{
  "vote": {
    "token": "fjosjfidsw",
    "party_id": 10,
    "election_id": "election_id",
    "candidate_ids": [
      1158,
      1077,
      1191
    ]
  },
  "g_private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo+2EFBBRiHoDJazdLO+dckpHDpwwQ\nLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF0SsocvKeJ5orgaMeC2kjkgf1gMec\nwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDohqkWpgguAOQnEzt07c2o5drH03km9\nnF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPAYLshpK+awmJ8upqAwy+7JHXPfVz/\nbeShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK0Gxym0UG1LodR9hp+EmWoem8HJqY\nE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AInswIDAQABAoIBAGZLg8WcQIaRNJJt\ngVAKH/BOdpWOobQUYOQ+NoV5eYgl0nzGtVVWoAFcnJ+eGObY2h3+RvxCLoMuA9Kr\n10mlrhVRw2zSsVcsaxwLIU+7yrKdp0NH19dMnQO4MUOO6RhW3feaH/vWTWZtrRA8\nRt4wMYGZHefQVFh9Skr+AQR1YxJqpvNAahOJuAkoK5wkMtOmDQFI9VYPARFH1tSL\nE1Rf9aQ4Y2ZGffZsr9i1adzrX0uAPFpXH5EZVwYx5hr/HPfP3xgiZ9aP4kJjHTwp\n4T1k5KYHN9mH6oQccGi9GNOPGZQagtid/g6IsWIgdiVOWyjoNT8jWBQLa7Kl57n6\n4x25uJECgYEA2xXcj1zxc1wjJpVDN7mOStbrk9ngLZRhU34UVxzCugbMFesBRO9X\n39u7t80D6Q7cJ9JE4LrBTYJd736k5oFp3Hzea4jmD4zPUKSRR8BD5dQ7th/XOcvo\njaEyoWD0kWblTqkAinfoKzt4HxEsBBAsIh0PyhgWz4yoBuI0LZgX44kCgYEA+ZGP\nWbfXm9ZrMWU3Owhdqr3J1YqJKNMa+ydQC2xxnv4LAbiSnKyAGACiAP8ymKceU0bA\nHtQUaLoYeMEJcJ6fSK9xFcrUB+VRxmvcG9zrwoYUjRMxSPoMh+r68vzGCpQ7ZcSQ\noLd67ncWD1X2uPeyqex83N+e++ih5q2IcUwillsCgYB3A89HikQYWQs3YIqdcQ3d\nlhdvwEJKQHsGsk02bYdTK3IezgVof2ULVQEK/jKLnuj2MQH92zY7dwC0o+XM2qy5\nfJQPctUXyXSt6FiL0+SOq9asP2vaF+2DUviANn1lp7IWIzUKA815/tpodhmlM2vm\nNEdpj+CEa3K0Gpoh0qfXkQKBgQCCwOB6APfVjeFbX8wwAZIRgp3cY1i5KuFX9KDb\nW1WsFy1tGWa27ymtaad3Hj1D/UrGFqtRe4u10so/eeOYPYL2cfStljbAbEUL0Dbh\n4j0jDVx3DTclJNyr2VDhPc4EfOUhzHp5uaeOiJXmMwOwpRXWMTC6B+8jzB4G3aQ+\nt8TnQQKBgQDCLjDCEc/l3KHQYfTpxX1EIvoqEJSIRUyXjuICj0kP+fBXcWiYEEd4\njJTryVRmIulyJTuxAhhBNXlHGIMPX2fmU7IGgRKO/2kvb2yLGTnfecUGwPL4YEGy\nw0yCPjyhu9/fpr1lDUJ0NN+GmpqplkqvXtYPLdJSIigDVW7Jn/stRQ==\n-----END RSA PRIVATE KEY-----",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs6lvNfr+Eo6Mt+mW95fh\njUbCRygCNok8Y8yIu502lpDiz3bNdR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7I\nEpRSmY1nElabMoBbU2vsPWBsu7WR31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPu\nRVtuHy/q2tD5sY2ekWJc1YsoeQ5JDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c\n2P4NpNgSJ2NT8aF/bDbu3sQk9QuQXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchq\nrYj5Xnql/wcrnyOhcgeKsOBieH/fETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG4\n7QIDAQAB\n-----END PUBLIC KEY-----"
}

```

VoteToBeEncrypted

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|vote|[Vote](#schemavote)|true|none|none|
|g_private_key_pem|string|true|none|none|
|public_key_pem|string|true|none|none|

<h2 id="tocS_VotesEncrypted">VotesEncrypted</h2>
<!-- backwards compatibility -->
<a id="schemavotesencrypted"></a>
<a id="schema_VotesEncrypted"></a>
<a id="tocSvotesencrypted"></a>
<a id="tocsvotesencrypted"></a>

```json
{
  "polling_place_id": 0,
  "votes": [
    {
      "encrypted_message": "36AMNvcpAWdHAXKCSWexgyjxrt7xeWwhOf+oUMBqip/C051EZWlN4N4x3hVPwwIQh/l78suUNYYYQBTkERPkuaZ40D1NV4LM7nb+DHcQ0nzGIFxHND3CIDkT9UOi1AmrqrCtyVMpDP1SI/2glHjbMsrw9VowA3L8hbf3U4wSF65ocF5IxN8mrOraXUopMcu+GgFKjBh3Y56yhZfxwr7go2YvQwph1HuLYVkkBi3ZAk+1DHCuQ+oQC3ivVJPF6SBOHPJIgLGM5NUsJwq5MUWSgxlr+iQI/g/uWbjkcS7M9uBZE6+QRTD++6sqZhHxc8RTLVtqAmrp0m1We6kf/Nrx7KdqagpHQz1vgZEf50L+kVgXf9PnX1THB7U+jVB0ogvM1fmZ+JvWURHt9ZhgdO1wZvzigQP6jTNZw5amzga2T+6/KwC47dxdnnT/l/fSBXzgAbsCNWCegJfTakvpsCNjWRlPKIvbPcGEIZDKBaMTz/zhKHqTgQV/f3qmlHgq+GYVPsyl95NVBFiiYwWxYWvJIl8RCREfx39t2bAx74YsJ4fT8G3u438l6BvT5DMrEbN3YlAS7gwuRt4j3AQUWmyzHesIW1o/pJd+5IpNYQ3ld6363iu5G4mC00lnImnSig==",
      "encrypted_object": "lb5B/LAg2/38mot9jYzRpa9O6YwrXDilpspPrGrnTKKYUXVfQ9JhW5JIGoP6FuQBXM2XzlcXkb90/VDK6+h/HeJKEUf81h/A/KiN4AZVBtRoHXOpq1gyRpFk7q5dhHzniStAPZOLruNtrAYmOoUNq3hmHLxs2KnRTMZiEc9kOefIS1vjPKFAClNCqKL++7orwvRPWGzmLMPbq6DFc/Sb7hXVlBMiUCmS2iMtz9mgs9IXheCqvcGYZQZOubFK3zjtqOvFEjuGACUZkuGbmxHEFgbBMCUPXOH933aP8eNY33+UIKSc2DSNKTOOySJNi3EolJmUhbQT5NIWXf9lE3jqXg=="
    }
  ]
}

```

VotesEncrypted

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|polling_place_id|integer|true|none|none|
|votes|[[VoteEncrypted](#schemavoteencrypted)]|false|none|none|

<h2 id="tocS_VotingData">VotingData</h2>
<!-- backwards compatibility -->
<a id="schemavotingdata"></a>
<a id="schema_VotingData"></a>
<a id="tocSvotingdata"></a>
<a id="tocsvotingdata"></a>

```json
{
  "polling_places": [],
  "parties": [],
  "key_pairs": [],
  "texts": {
    "elections_name_short": {
      "sk": "string",
      "en": "string"
    },
    "elections_name_long": {
      "sk": "string",
      "en": "string"
    },
    "election_date": {
      "sk": "string",
      "en": "string"
    }
  }
}

```

VotingData

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|polling_places|[[PollingPlace](#schemapollingplace)]|false|none|none|
|parties|[[Party](#schemaparty)]|false|none|none|
|key_pairs|[[KeyPair](#schemakeypair)]|false|none|none|
|texts|[Texts](#schematexts)|true|none|none|

