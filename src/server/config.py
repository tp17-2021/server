SEED = 1
ELECTION_ID = "election_id"
CANDIDATES_JSON = "data/nrsr_2020/candidates_transformed.json"
PARTIES_JSON = "data/nrsr_2020/parties_transformed.json"
POLLING_PLACES_JSON = "data/nrsr_2020/polling_places.json"
ES_SYNCHRONIZATION_BATCH_SIZE = 50000 # in production set to 10000 and repeat every minute
PARLIAMENTS_SEATS_TO_SPLIT = 150
PARLIAMENT_ACCEPTANCE_THRESHOLD = 5
ELASTIC_RESULTS_LIMIT = 3 # in production set to 100000
