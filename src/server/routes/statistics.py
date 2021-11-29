from fastapi import APIRouter

from src.server.database import DB, CLIENT

# Create FastAPI router
router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
)


@router.get('/progress')
async def statistics_progress():
    votes = list(DB.votes.find({}))
    eligible_voters = 2 * (10**3) # in conf
    vote_participation = round(eligible_voters / len(votes), 5) if len(votes) else 0

    offices = DB.election_offices.find({}).count()
    open_offices = 0
    closed_offices = offices - open_offices
    
    return {
        'status' : 'success',
        'message': 'Voting progress statistics',
        'statistics' : {
            "votes" : len(votes),
            "eligible_voters" : eligible_voters,
            "vote_participation" : vote_participation,
            "offices" : offices,
            "open_offices" : open_offices,
            "closed_offices" : closed_offices
        }
    }
