import praw
import pandas as pd
import re

# -------------------------
# CONFIG
# -------------------------
import os

CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
USER_AGENT = os.environ["REDDIT_USER_AGENT"]
print('client id ', CLIENT_ID)
print('client secret ', CLIENT_SECRET)
print('user agent ', USER_AGENT)
COLLEGE = "IIFT"
SEARCH_QUERY = f"{COLLEGE} interview experience"
SUBREDDITS = ["MBA", "gradadmissions", "Indian_Academia", "GMAT", "CATPreparation"]

POST_LIMIT = 200

# patterns indicating interview questions
QUESTION_PATTERNS = [
    r"they asked me (.+)",
    r"i was asked (.+)",
    r"question was (.+)",
    r"one question (.+)",
    r"asked about (.+)"
]

# -------------------------
# INIT REDDIT
# -------------------------

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

results = []

# -------------------------
# EXTRACT QUESTIONS
# -------------------------

def extract_questions(text):

    text = text.lower()
    sentences = re.split(r'[.!?]', text)

    extracted = []

    for sentence in sentences:
        for pattern in QUESTION_PATTERNS:
            match = re.search(pattern, sentence)
            if match:
                extracted.append(sentence.strip())

    return extracted


# -------------------------
# SCRAPE POSTS
# -------------------------

for sub in SUBREDDITS:

    subreddit = reddit.subreddit(sub)

    for post in subreddit.search(SEARCH_QUERY, limit=POST_LIMIT):

        content = post.title + " " + post.selftext

        # extract from post
        questions = extract_questions(content)

        for q in questions:
            results.append({
                "college": COLLEGE,
                "source": "post",
                "text": q,
                "url": post.url
            })

        # extract from comments
        post.comments.replace_more(limit=0)

        for comment in post.comments.list():

            questions = extract_questions(comment.body)

            for q in questions:
                results.append({
                    "college": COLLEGE,
                    "source": "comment",
                    "text": q,
                    "url": post.url
                })


# -------------------------
# SAVE DATA
# -------------------------

df = pd.DataFrame(results)

df.drop_duplicates(inplace=True)

df.to_csv(f"{COLLEGE}_interview_questions.csv", index=False)

print("Saved", len(df), "questions")
