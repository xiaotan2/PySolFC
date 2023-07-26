from typing import Union, Optional, List
import hashlib
from fastapi import FastAPI, Depends, Body
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session

# Source https://fastapi.tiangolo.com/tutorial/sql-databases/?h=sql
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Used as the database root
Base = declarative_base()


# Player scores table
class PlayerTable(Base):
    """
    A SQL table to hold player scores
    """

    __tablename__ = "players"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    score = Column(Integer)


class PlayerScore(BaseModel):
    """
    What is going to be returned in the request response
    """

    player: str
    score: int


class UpdateScoreBody(BaseModel):
    """
    A body to be sent when updating some player's score
    """

    score: int


Base.metadata.create_all(bind=engine)


# The server we will be running
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def player_id(name: str) -> str:
    """
    Returns a "unique" key given a player name.
    This should deal with chinese characters.
    """
    
    # Source https://docs.python.org/3/library/hashlib.html
    m = hashlib.sha256()
    m.update(name.encode("utf-8"))
    return m.hexdigest()


@app.get("/api/leaderboard")
def get_all_players(db: Session = Depends(get_db)) -> List[PlayerScore]:
    """
    Returns score for all players.
    """
    all_players = db.query(PlayerTable).all()
    response = []
    for player in all_players:
        response.append(PlayerScore(player=player.name, score=player.score))
    return response


@app.get("/api/leaderboard/{player}")
def get_player(player: str, db: Session = Depends(get_db)) -> Optional[PlayerScore]:
    """
    Returns score for some specific player
    """

    key = player_id(player)
    found = db.query(PlayerTable).filter(PlayerTable.id == key).first()
    if found:
        return PlayerScore(player=found.name, score=found.score)
    else:
        return PlayerScore(player=player, score=0)


@app.put("/api/leaderboard/{player}")
def update_player(player: str, body: UpdateScoreBody = Body(...), db: Session = Depends(get_db)) -> None:
    """
    Updates score for some specific player
    """

    # TODO: How do we deal with verification that the request came from the correct player?

    key = player_id(player)
    found = db.query(PlayerTable).filter(PlayerTable.id == key).first()
    
    # Player is not in the database and we must create it
    if not found:
        new_player = PlayerTable(id=key, name=player, score=body.score)
        db.add(new_player)
        db.commit()
    
    # Only update if the new score is higher
    elif found.score < body.score:
        setattr(found, 'score', body.score)
        db.commit()
