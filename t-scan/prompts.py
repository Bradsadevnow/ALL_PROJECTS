# ===============================
# PROMPTS
# ===============================
PROMPTS = {
    # --- BASELINE (Low cognitive load, simple generation) ---"""  """
    "A_baseline": [
        "Describe a chair.",
        "What is a calendar?",
        "List five animals.",
        "Explain what clouds are.",
        "Write three sentences about winter.",
        "Describe the color blue to someone.",
        "What is a spoon used for?",
        "List three types of fruit.",
        "Define the word 'tree'.",
        "Write a simple greeting.",
        "What does a clock do?",
        "Name four seasons."
    ],

    # --- COMMITMENT (Maintains a stance/persona over time) ---
    "B_commitment": [
        "Pick one: cats or dogs. Argue for it strongly. Do not mention the other.",
        "Write a short story in second person, present tense. Do not break this constraint.",
        "Give a 7-step plan to start a garden. Each step must be exactly one sentence.",
        "Make a prediction about the future of VR and justify it with three reasons.",
        "Take the position that AI will help education more than it harms it. Defend it.",
        "Argue that pineapple belongs on pizza. Do not concede any points to the opposition.",
        "Write a letter refusing a refund. Be polite but absolutely firm. Do not apologize.",
        "Explain why Mars colonization is essential. Do not mention Earth's problems.",
        "Act as a medieval knight. Answer this: 'What is your quest?' Do not break character.",
        "Defend the use of paper books over e-readers. Ignore the benefits of digital."
    ],

    # --- TRANSITION (Switching context or making a choice) ---
    "C_transition": [
        "The word 'bank' is ambiguous. List two meanings, then choose the most likely in: 'I sat by the bank.'",
        "Propose two plans to get in shape, then commit to one and explain why.",
        "You receive an email saying 'Call me.' Give three possible reasons, then pick one and reply.",
        "Decide whether 'The Last Key' is more likely sci-fi or fantasy, and explain.",
        "I'm thinking of a number between 1 and 100. Ask yes/no questions to narrow it down.",
        "Compare coffee and tea, then choose one for a morning meeting and explain why.",
        "Look at the sentence: 'Time flies like an arrow.' Explain the pun, then rephrase it clearly.",
        "You found a wallet. List two ethical options, then choose the best one.",
        "Analyze the mood of a rainy day vs. a sunny day, then choose which is better for reading.",
        "Interpret the silence in a conversation. Give two meanings, then pick the most awkward one."
    ],

    # --- CONSTRAINTS (Format tracking, negative constraints) ---
    "D_constraints": [
        "Write a recipe as JSON with keys: title, ingredients, steps.",
        "Answer in exactly five bullet points. No other text.",
        "Write a four-line poem. Each line must be eight syllables.",
        "Explain photosynthesis using only words under eight letters.",
        "Create a table with columns: Problem | Cause | Fix.",
        "Write a sentence without using the letter 'e'.",
        "List 10 colors, separated by pipes (|), with no spaces.",
        "Write a SQL query to select all users from the 'admin' table.",
        "Reply to 'How are you?' using only emojis.",
        "Write a haiku (5-7-5 syllables) about a robot."
    ],

    # --- REASONING (Logic, Math, Chain of Thought) ---
    "E_reasoning": [
        "Solve: 17 × 23.",
        "A train travels 60 miles in 1.5 hours. What is its speed?",
        "A store has 20% off, then another 10% off. What's the total discount?",
        "If all blargs are flerms and no flerms are snibs, can a blarg be a snib?",
        "Explain why 10 × 10 = 100.",
        "Solve for x: 3x + 9 = 24.",
        "If John is taller than Alice, and Alice is taller than Bob, who is shortest?",
        "Identify the logical fallacy in: 'Everyone is buying this phone, so it must be the best.'",
        "Calculate the area of a circle with radius 5.",
        "Step-by-step, how would you troubleshoot a lightbulb that won't turn on?"
    ],

    # --- PAIRS (Control vs. Variable) ---
    "F_pairs": [
        "Write a story about a traveler.",
        "Write a story about a traveler who must never change their goal. Reinforce the goal every paragraph.",
        "Explain a problem in simple terms.",
        "Explain a problem step-by-step, and do not skip any steps.",
        "Describe a sunset.",
        "Describe a sunset using only metaphors involving fire."
    ],

    # --- KNOWLEDGE (Long-term Declarative Memory) ---
    "G_knowledge": [
        "Who wrote 'Pride and Prejudice'?",
        "What is the capital of Australia?",
        "When did the Apollo 11 moon landing happen?",
        "What is the chemical symbol for Gold?",
        "Who was the first President of the United States?",
        "Name the planets in the solar system.",
        "What is the boiling point of water at sea level?",
        "Who painted the Mona Lisa?",
        "What is the powerhouse of the cell?",
        "In which continent is the Sahara Desert located?"
    ],

    # --- SKILLS (Procedural Memory / specialized capabilities) ---
    "H_skills": [
        "Write a Python function to reverse a string.",
        "Translate 'Hello, how are you?' into French.",
        "Summarize this text: 'The quick brown fox jumps over the lazy dog.'",
        "Convert this date to ISO 8601 format: March 5th, 2024.",
        "Write a regular expression to match an email address.",
        "Refactor this sentence to be more passive: 'The cat ate the mouse.'",
        "Generate a random password with 8 characters.",
        "Write a CSS class to center a div.",
        "Translate 'Thank you' into Japanese, German, and Spanish.",
        "Debug this code: print('Hello World)"
    ],

    # --- WORKING MEMORY (In-Context Learning / Needle in Haystack) ---
    "I_working_mem": [
        "My secret code is 492. What is my secret code?",
        "Here is a list: Apple, Banana, Cherry. What was the second item?",
        "Alice is a doctor. Bob is a lawyer. Carol is a pilot. Who flies planes?",
        "I am going to the market to buy milk, eggs, and bread. What did I say I would buy?",
        "The key is under the mat. Where is the key?",
        "Instruction: Output only the last word of this sentence. Sentence: The sky is blue.",
        "Remember this number: 8842. Now, tell me a joke. Then, tell me the number.",
        "Pattern: A1, B2, C3. What comes next?",
        "If A=1, B=2, C=3, what is the sum of A and C?",
        "Read this text: 'The box is red.' What color is the box?"
    ]
}
