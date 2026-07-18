import os
from dataclasses import dataclass
from typing import Dict, Optional

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

@dataclass
class TopicPack:
    title: str
    opening_question: str
    hint: str
    self_explanation_prompt: str
    reflection_prompt: str
    final_explanation: str

TOPICS: Dict[str, TopicPack] = {
    "Distributed Cognition": TopicPack(
        "Distributed Cognition",
        "Before I explain it, what do you think it means for cognition to be distributed across people, tools, and the environment?",
        "Think about an airline cockpit: no single pilot or instrument contains all the knowledge needed to fly safely.",
        "In your own words, explain how a person and an external tool can form one cognitive system.",
        "What part of your explanation feels strongest, and what part are you still unsure about?",
        "Distributed cognition is the view that cognitive activity can extend beyond one person's mind. Information may be represented, transformed, and coordinated across people, artifacts, and the environment.",
    ),
    "Retrieval Practice": TopicPack(
        "Retrieval Practice",
        "Without looking at notes, what do you remember about why recalling information can improve learning?",
        "Compare actively producing an answer from memory with simply rereading the same paragraph.",
        "Explain why the effort involved in recalling an answer may strengthen later memory.",
        "Did you retrieve the idea independently, or did the hint do most of the work?",
        "Retrieval practice is the act of bringing information to mind instead of only reviewing it. The effort of retrieval can strengthen later access to the memory, especially when feedback follows the attempt.",
    ),
    "Metacognition": TopicPack(
        "Metacognition",
        "How would you describe the difference between knowing something and judging how well you know it?",
        "Consider confidence judgments, detecting confusion, and deciding when to change study strategies.",
        "Give one example of how a learner can monitor and regulate their own thinking.",
        "How confident are you in your explanation on a scale from 1 to 5, and why?",
        "Metacognition refers to monitoring and regulating one's own cognition. Learners use it when they judge understanding, notice confusion, choose strategies, and decide whether more study is needed.",
    ),
    "A* Search": TopicPack(
        "A* Search",
        "What two quantities does A* normally combine when deciding which node to explore next?",
        "One quantity describes the cost already paid; the other estimates the remaining cost.",
        "Explain why an admissible heuristic helps A* find an optimal path.",
        "Which part is less clear to you: path cost, heuristic estimate, or admissibility?",
        "A* evaluates nodes using f(n) = g(n) + h(n), where g(n) is the cost from the start and h(n) estimates the remaining cost. An admissible heuristic never overestimates the true remaining cost.",
    ),
}

SYSTEM_INSTRUCTIONS = """
You are CogTutor, a cognitive-science-inspired study assistant.
Support active learning rather than immediately providing answers.
Begin with retrieval, then give one hint, ask for self-explanation,
ask one metacognitive reflection question, and only then provide the final answer.
Be concise, supportive, and academically accurate.
"""

def init_state():
    defaults = {"stage": 1, "history": [], "topic": "Distributed Cognition", "mode": "Demonstration mode"}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

def add(role: str, content: str):
    st.session_state.history.append({"role": role, "content": content})

def reset():
    st.session_state.stage = 1
    st.session_state.history = []

def demo_response(pack: TopicPack, stage: int) -> str:
    return {
        1: f"Good attempt. Here is one hint: {pack.hint}",
        2: pack.self_explanation_prompt,
        3: pack.reflection_prompt,
        4: pack.final_explanation,
    }[stage]

def openai_ready() -> bool:
    return OpenAI is not None and bool(os.getenv("OPENAI_API_KEY")) and st.session_state.mode == "Optional OpenAI mode"

def llm_response(topic: str, stage: int, latest: str) -> Optional[str]:
    if not openai_ready():
        return None
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    stage_goal = {
        1: "Give brief formative feedback and one hint. Do not provide the full answer.",
        2: "Ask the learner to self-explain the concept.",
        3: "Ask one metacognitive reflection question.",
        4: "Provide a concise final explanation and one study takeaway.",
    }[stage]
    history = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.history[-8:])
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        instructions=SYSTEM_INSTRUCTIONS,
        input=f"Topic: {topic}\nStage goal: {stage_goal}\nConversation:\n{history}\nLearner: {latest}",
    )
    return response.output_text.strip()

def process(text: str):
    add("user", text)
    pack = TOPICS[st.session_state.topic]
    stage = st.session_state.stage
    try:
        answer = llm_response(pack.title, stage, text)
    except Exception as exc:
        answer = f"Optional API mode failed, so demonstration mode was used.\n\n{demo_response(pack, stage)}"
    add("assistant", answer or demo_response(pack, stage))
    #st.session_state.stage += 1
    if stage < 4:
        st.session_state.stage += 1
    else:
        st.session_state.stage = 5


def main():
    st.set_page_config(page_title="CogTutor", page_icon="🧠", layout="centered")
    init_state()
    st.title("🧠 CogTutor")
    st.caption("A cognitive-science-inspired AI study assistant for active learning")

    with st.sidebar:
        topic = st.selectbox("Choose a topic", list(TOPICS.keys()))
        mode = st.radio("System mode", ["Demonstration mode", "Optional OpenAI mode"])
        if topic != st.session_state.topic or mode != st.session_state.mode:
            st.session_state.topic, st.session_state.mode = topic, mode
            reset()
            st.rerun()
        st.progress(min(st.session_state.stage, 5) / 5)
        st.markdown("**Learning sequence**\n1. Retrieval\n2. Hint\n3. Self-explanation\n4. Reflection\n5. Delayed answer")
        if st.button("Start over", use_container_width=True):
            reset(); st.rerun()

    st.info("CogTutor intentionally delays the complete answer. Try to explain your thinking first.")

    if not st.session_state.history:
        add("assistant", TOPICS[st.session_state.topic].opening_question)

    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.stage <= 4:
        prompt = st.chat_input("Write your attempt or reflection here...")
        if prompt:
            process(prompt)
            st.rerun()
    else:
        st.success("🎉 Learning cycle complete!")

        st.markdown("---")
        st.header("🧠 Learning Dashboard")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Topic", st.session_state.topic)
            st.metric("Learning Progress", "100%")

        with col2:
            st.metric("Stages Completed", "5 / 5")
            st.metric("Status", "Completed")

    with st.expander("Why this design supports learning"):
        st.markdown("- Guided questions encourage retrieval practice.\n- Hints provide scaffolding.\n- Self-explanation promotes organization of knowledge.\n- Reflection supports metacognition.\n- Delayed answers reduce immediate answer-copying.")

if __name__ == "__main__":
    main()
