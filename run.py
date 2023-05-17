from app import app, db, socket, redis_db
import os

if __name__ == "__main__":
    db.create_all()
    socket.run(app, debug = True)
    redis_db.dropDatabase()