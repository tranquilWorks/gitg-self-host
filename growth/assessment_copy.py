"""Display-only wording, keyed by frozen v1.1 IDs; never an input to scoring.

Keep polarity, comparisons, time frame and scale anchors aligned with the
canonical items. The canonical spec and scorer are deliberately not rewritten.
"""

PROMPTS = {
    "Q01": "When I face a new problem, I want to understand how it works before I act.",
    "Q02": (
        "I enjoy spotting patterns, finding things that do not add up, and working out "
        "the most accurate explanation."
    ),
    "Q03": (
        "When an important decision is stuck, I would rather take responsibility for a "
        "workable choice than keep asking for more input."
    ),
    "Q04": "Starting something difficult gives me energy, even when others may judge the result.",
    "Q05": (
        "When a group has trouble with both its task and its relationships, I first "
        "notice whether people feel heard and included."
    ),
    "Q06": (
        "With the same amount of free time, I would rather build or repair a relationship "
        "than work alone on an idea or project."
    ),
    "Q07": (
        "I naturally look after routines, promises, and resources so people can keep "
        "relying on them."
    ),
    "Q08": (
        "I would rather strengthen an important responsibility or a proven way of doing "
        "things than leave it for something new."
    ),
    "Q09": "Even when a good method already exists, I want to try an unfamiliar alternative.",
    "Q10": (
        "Exploring unfamiliar subjects, places, or ways of doing things gives me energy, "
        "even without an immediate practical benefit."
    ),
    "Q11": (
        "When something benefits me but conflicts with a principle or a wider good I "
        "believe in, I think first about the principle or wider good."
    ),
    "Q12": (
        "Questions about meaning, living well, what is sacred, beauty, or what I will "
        "leave behind give me energy."
    ),
    "Q13": "When important choices compete, I can explain which one best fits my purpose in life.",
    "Q14": (
        "I follow the same standards of right and wrong whether they cost me something or "
        "benefit me."
    ),
    "Q15": (
        "I regularly do something that connects me to meaning, what I hold sacred, or a "
        "reality beyond my own immediate interests."
    ),
    "Q16": (
        "After a loss or serious setback, I can face what happened without denying it and "
        "still find a reason to keep going."
    ),
    "Q17": "I notice my usual ways of defending myself before they take over how I behave.",
    "Q18": "I can name the emotion I feel, how strong it is, and what set it off.",
    "Q19": (
        "When I am very upset, I can calm down enough to choose a response I can still "
        "stand by later."
    ),
    "Q20": (
        "I can stay focused on the person or task I chose, even when something easier or "
        "more stimulating is available."
    ),
    "Q21": (
        "When I strongly want pleasure, approval, comfort, or escape, I can pause long "
        "enough to make a deliberate choice."
    ),
    "Q22": "I start and finish important work on time, even when I do not feel motivated.",
    "Q23": (
        "When a plan fails, I change it quickly without clinging to it or giving up on "
        "the goal without thinking."
    ),
    "Q24": (
        "I can work out what a claim assumes and how its reasons are meant to support its "
        "conclusion."
    ),
    "Q25": (
        "When trustworthy evidence challenges a belief I care about, I change the belief "
        "instead of brushing the evidence aside."
    ),
    "Q26": (
        "Before an important decision, I think about later effects, what I gain and give "
        "up, how effects may feed back on each other, and what could go wrong."
    ),
    "Q27": (
        "When learning something difficult, I test what I remember, practise, and use "
        "feedback instead of mostly rereading or watching explanations."
    ),
    "Q28": (
        "I regularly make something, or interpret someone else's work, using both learned "
        "skills and my own judgment."
    ),
    "Q29": (
        "I keep health routines that reliably support my energy and ability to do "
        "physical activities."
    ),
    "Q30": (
        "I can manage a household on my own: keeping it clean, safe, supplied with food, "
        "and working."
    ),
    "Q31": (
        "I use digital tools deliberately enough to protect my information and avoid "
        "letting the tools steer my choices without me noticing."
    ),
    "Q32": (
        "I can spot common dangers and follow a sensible plan for emergencies or risky situations."
    ),
    "Q33": (
        "The way I manage money reliably covers my bills, risks I can plan for, and "
        "long-term goals."
    ),
    "Q34": (
        "When I want to create something that is worth money, I can test whether it "
        "meets a real need and adapt using feedback."
    ),
    "Q35": (
        "In difficult conversations, I can explain what I mean and accurately sum up the "
        "other person's view before I respond."
    ),
    "Q36": (
        "I can imagine how a situation looks to someone else and check whether I "
        "understood, rather than assuming I am right."
    ),
    "Q37": (
        "I state my limits clearly and follow through on them, even when someone may feel "
        "disappointed or disapprove."
    ),
    "Q38": (
        "I regularly reach out, make time, and give back in important relationships "
        "instead of waiting for others to do the work."
    ),
    "Q39": (
        "In intimate relationships, I speak honestly about desire, consent, expectations, "
        "and things that leave me feeling vulnerable."
    ),
    "Q40": (
        "When someone depends on me, I give reliable care while respecting their choices "
        "and my own limits."
    ),
    "Q41": (
        "After harm in a relationship, I can take responsibility for my part, try to "
        "repair it, and recognize that forgiveness does not automatically restore trust."
    ),
    "Q42": (
        "On an issue that matters to me, I can find the organization responsible and take "
        "a practical step as a citizen or community member."
    ),
    "Q43": (
        "I treat people with dignity and fairness, even when I dislike them or disagree "
        "with their group."
    ),
    "Q44": "I reliably do useful, high-quality work and understand who depends on it.",
    "Q45": (
        "When I am responsible for others, I give clear direction, welcome disagreement, "
        "and avoid controlling more than I need to."
    ),
    "Q46": (
        "I regularly rest, play, or celebrate without turning it into another thing to "
        "improve or a way to numb myself and escape."
    ),
    "Q47": (
        "I choose to spend time in unfamiliar places or nature, with curiosity and "
        "preparation that fits the situation."
    ),
    "Q48": (
        "My calendar, commitments, and surroundings match what I say matters in this part "
        "of my life."
    ),
    "Q49": (
        "I deliberately pass on knowledge, care, opportunities, or lasting work so it "
        "keeps helping after I am no longer involved."
    ),
    "Q50": (
        "I answered based on what I have actually done in the past six months, not mainly "
        "on who I hope or think I should be."
    ),
    "C_L01": (
        "I can name the few commitments that should come first when important demands compete."
    ),
    "C_L02": "I keep my promises and standards even when nobody would know if I did not.",
    "C_L03": (
        "My spiritual beliefs or quiet reflection shape real choices, rather than staying as ideas."
    ),
    "C_L04": (
        "I can live with grief, uncertainty, or suffering without playing it down or "
        "losing all hope."
    ),
    "C_L05": (
        "When feedback from someone I trust challenges how I see myself, I can consider "
        "it without immediately defending myself."
    ),
    "C_L06": (
        "I can tell the difference between what I feel, what I think happened, and what I "
        "want to do next."
    ),
    "C_L07": (
        "After something shakes up my life, I can rebuild routines and adapt without "
        "getting stuck avoiding it or acting on impulse."
    ),
    "C_L08": (
        "I notice when my attention wanders and can bring it back without needing "
        "something new to stimulate me."
    ),
    "C_L09": "I can enjoy myself without repeatedly going beyond limits I chose beforehand.",
    "C_L10": (
        "I keep up important routines through everyday disruptions, not only when I feel motivated."
    ),
    "C_L11": (
        "I can keep doing what is needed when plans, roles, or expectations change unexpectedly."
    ),
    "C_L12": "I can spot when the reasons given do not actually support the conclusion.",
    "C_L13": (
        "Before I repeat a claim, I check where it came from, how good the evidence is, "
        "what is uncertain, and other possible explanations."
    ),
    "C_L14": (
        "I can tell a sign of a problem from its underlying cause and choose a change "
        "that tackles how the problem keeps happening."
    ),
    "C_L15": "After time has passed, I can teach or use what I learned in a different situation.",
    "C_L16": (
        "I finish and share creative work instead of stopping at inspiration, "
        "preferences, or unfinished drafts."
    ),
    "C_L17": (
        "I can adjust exercise, food, sleep, and medical care using signs from my body "
        "and qualified advice."
    ),
    "C_L18": (
        "I can work out everyday household problems and recognize when I need professional help."
    ),
    "C_L19": (
        "I can spot misleading or poor-quality digital information before I act on it or share it."
    ),
    "C_L20": (
        "I keep emergency knowledge, supplies, and plans that realistically fit where I "
        "live and spend time."
    ),
    "C_L21": (
        "I know how much money comes in and goes out, what I owe, what I have set aside, "
        "what my insurance covers, and my long-term money plan."
    ),
    "C_L22": (
        "For a money-related decision or business idea, I understand what motivates the "
        "people involved, the costs, the customers, and what must be given up."
    ),
    "C_L23": (
        "After a difficult conversation, people usually know what I meant and feel that I "
        "understood them."
    ),
    "C_L24": (
        "I change my judgment of someone when their account or new evidence shows that my "
        "first impression was wrong."
    ),
    "C_L25": (
        "I can say no, ask for something, or address disrespect without giving in, "
        "apologizing for having a limit, or becoming aggressive."
    ),
    "C_L26": (
        "I regularly give my close relationships time, effort, reliability, and practical support."
    ),
    "C_L27": (
        "I can calmly talk about sexual and relationship boundaries before confusion or "
        "pressure causes a problem."
    ),
    "C_L28": (
        "I can organize care, responsibilities, and limits without controlling or "
        "abandoning the person who depends on me."
    ),
    "C_L29": (
        "When the same conflict keeps happening, I change the pattern behind it instead "
        "of only apologizing each time."
    ),
    "C_L30": (
        "I take informed action in my community or public life, rather than only having "
        "opinions or getting angry."
    ),
    "C_L31": (
        "I can stand up for fairness while describing opposing views honestly and "
        "refusing to treat other people as less than human."
    ),
    "C_L32": (
        "I improve my work through clear standards, focused practice, feedback, useful "
        "records, and doing what I promised on time."
    ),
    "C_L33": (
        "People I am responsible for become clearer about what to do, safer, and more "
        "capable, rather than just relying on me more."
    ),
    "C_L34": (
        "I can be fully present when resting or celebrating, then return to "
        "responsibilities without guilt or avoiding them."
    ),
    "C_L35": (
        "I seek challenges and new experiences without mistaking recklessness, newness "
        "alone, or buying things for personal growth."
    ),
    "C_L36": (
        "As my life changes, I deliberately rebalance work, relationships, health, "
        "helping others, and rest."
    ),
    "C_L37": (
        "I build up people, systems, traditions, or records that keep helping without "
        "needing me there all the time."
    ),
    "O_DISC": (
        "I would rather pause briefly to understand a problem better than act immediately "
        "with an incomplete picture."
    ),
    "O_AGEN": (
        "I would rather take responsibility for a difficult decision and its results than "
        "wait for someone else to resolve it."
    ),
    "O_CONN": (
        "I would rather work toward understanding each other than win a minor argument or "
        "get the best possible task result."
    ),
    "O_STEW": (
        "I would rather look after an important responsibility well than chase a new "
        "opportunity that might weaken it."
    ),
    "O_EXPL": (
        "I would rather explore several reasonable options than commit early to the first "
        "one that works."
    ),
    "O_TRAN": (
        "I would accept a real personal cost for a principle or a shared good I deeply believe in."
    ),
}

SCALES = {
    "orientation": {
        "1": "Least like me",
        "2": "Usually not like me",
        "3": "Sometimes like me; it depends on the situation",
        "4": "Usually like me",
        "5": "Most like me",
    },
    "capability": {
        "1": "Rarely; I usually need a lot of guidance",
        "2": "Sometimes, with reminders, a clear plan, or support",
        "3": "Usually, in familiar situations without much pressure",
        "4": "Reliably, across everyday situations",
        "5": "Reliably, even under pressure or in new situations; I can adapt or help others",
    },
    "response_quality": {
        "1": "Strongly disagree",
        "2": "Disagree",
        "3": "Partly agree and partly disagree",
        "4": "Agree",
        "5": "Strongly agree",
    },
}


def assessment_display_copy():
    return {"prompts": PROMPTS, "scales": SCALES}
