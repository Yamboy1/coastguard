from lxml import etree
from lxml.builder import E

import db
from db import LevelScore, GameInfo, Medals

username = "USERNAME"
token = "TOKEN"

legowebsiteurl = "http://city.lego.com/Products/CoastGuard/Default.aspx"
loginurl = "https://account.lego.com/Signin.aspx?ReturnUrl=http://city.lego.com/games/coastguard.aspx"
getbadgeurl = "http://mln.lego.com"


def gettoken() -> list[etree._Element]:
    db.init_scores(username)
    return [
        E.token(token),
        E.username(username),
    ]


def getlinkurls() -> list[etree._Element]:
    return [
        E.data(
            E.legowebsiteurl(legowebsiteurl),
            E.loginurl(loginurl),
            E.getbadgeurl(getbadgeurl),
        )
    ]


def getscore() -> list[etree._Element]:
    game_info = db.load_scores()

    return [
        E.data(
            E.levelsunlocked(str(game_info.levelsunlocked)),
            E.currentrank(str(game_info.currentrank)),
            E.totalscore(str(game_info.totalscore)),
            *(
                E.level(
                    {"levelnumber": str(level_info.level)},
                    E.score(str(level_info.score)),
                    E.medals(str(level_info.medals)),
                )
                for level_info in game_info.levels
            ),
        )
    ]


def savescore(root: etree._Element) -> list[etree._Element]:
    levels = [
        LevelScore(
            level=int(level.get("levelnumber", "")),
            score=int(level.findtext("score", "")),
            medals=Medals(int(level.findtext("medals", ""))),
        )
        for level in root.findall("data/level")
    ]

    game_info = GameInfo(
        username=username,
        levelsunlocked=int(root.findtext("data/levelsunlocked", "")),
        currentrank=int(root.findtext("data/currentrank", "")),
        totalscore=int(root.findtext("data/totalscore", "")),
        levels=levels,
    )
    db.save_scores(game_info)

    return []
