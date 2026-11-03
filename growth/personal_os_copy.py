"""Display-only planning prompts; stored IDs and contract definitions stay frozen."""

PROMPTS = {
    "mission": (
        "What would you like to contribute?",
        "For example: help my family feel supported, or make useful things. "
        "This is a planning reminder, not text the app analyzes or scores.",
    ),
    "principles": (
        "What rules of thumb do you want to live by?",
        "Write one to five of your own, one per line—not choices from a hidden list. "
        "For example: ask before assuming; protect time for friends.",
    ),
    "anti_goals": (
        "What do you want to avoid building your life around?",
        "Write one to five patterns, one per line. For example: being available for work "
        "all evening. Use these as boundaries when planning.",
    ),
    "twelve_month_direction": (
        "What would you like to change over the next year?",
        "For example: build a dependable circle of friends. This reminder appears when you "
        "plan; it does not automatically change recommendation scores.",
    ),
    "priority_stack": (
        "What deserves your attention first?",
        "Write one to five priorities in order, one per line. "
        "You can explicitly connect a practice to one of these later.",
    ),
    "current_truth": (
        "What is your situation right now?",
        "A short description can help you compare your intentions with daily life. "
        "Only include details you want to keep.",
    ),
    "autopilot_pattern": (
        "What are you doing mainly out of habit or pressure?",
        "Name a recurring pattern you might want to choose more deliberately. "
        "This reflection is not scored.",
    ),
    "misalignment_or_fragmentation": (
        "Where is your time going somewhere you do not want?",
        "Think of one commitment or habit that competes with what matters to you. "
        "This is for your review, not an automatic judgment.",
    ),
    "deliberate_next_step": (
        "What small step would help you decide what comes next?",
        "Choose something concrete, such as talking to a friend or protecting an hour "
        "this week. Writing it here does not mark a practice complete.",
    ),
}
