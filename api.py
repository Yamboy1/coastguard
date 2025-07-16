from lxml import etree
from lxml.builder import E

import db
import mln
from db import LevelScore, GameInfo, Medals

legowebsiteurl = "http://city.lego.com/Products/CoastGuard/Default.aspx"


def gettoken(session_id: str, username: str | None) -> list[etree._Element]:
    if not username:
        return [E.token(session_id)]

    db.init_scores(username)
    return [
        E.token(session_id),
        E.username(username),
    ]


def getlinkurls(session_id: str) -> list[etree._Element]:
    return [
        E.data(
            E.legowebsiteurl(legowebsiteurl),
            E.loginurl(mln.get_login_url(session_id)),
            E.getbadgeurl(mln.MLN_MAILBOX_URL),
        )
    ]


def getscore(username: str | None) -> list[etree._Element]:
    if not username:
        game_info = GameInfo(username="", levels=[])
    else:
        game_info = db.load_scores(username)

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


def savescore(
    session_id: str, username: str | None, root: etree._Element
) -> list[etree._Element]:
    if not username:
        return []

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
    mln.submit_rank(session_id, game_info.currentrank)

    return []
