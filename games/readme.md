This acts as our interim games database while I figure out dynamodb

Each game is stored as a json, {GAME-ID}.json, in the following format:



    {
        "id":id(string),
        "players" :[
            {
                "id": id(string),
                "name": name(string),
                "scores": [ score (float) ],
                "results": { problem results go here },
                "last_submit": 0|seconds since epoch,
            },
        ]
        "status": "waiting|started|ended",
        "start_time": -1|seconds since epoch,
        "duration": -1|num minutes,
        "problems": ["problemname", ],
    }