Grading results for each submission are stored in `[submission id].json`, in the following format

    {
        "submission": [submission id],
        "problem": [problem id],
        "status": [waiting|grading|graded],
        "code": [code],
        "lang": [language],
        "results": [
            [
                [WA | AC | TLE | RE], [run time]
            ], for each test case
        ]
    }