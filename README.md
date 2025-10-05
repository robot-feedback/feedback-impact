
[**Code**](https://github.com/robot-feedback/feedback-impact/tree/main/code)
| [**LLM Prompt**](https://github.com/robot-feedback/feedback-impact/tree/main/llm_prompt/)
| [**Feedback Data**](https://github.com/robot-feedback/feedback-impact/tree/main/generated_feedback/)
| [**User Study Questionnares**](https://github.com/robot-feedback/feedback-impact/tree/main/supplementary_files)

# Impact of Adaptive Robot Feedback on Human Task Performance

![Feedback Study Design](./project_images/feedback_study_design.png)

## Overview
This project investigates how adaptive robot feedback, powered by large language models (LLMs)- influences human task performance and perception across different task types and agent embodiments.
We explore how varying feedback levels (task-learning, task-motivation, self-level and no feedback) interact with promotion- vs. prevention-focused tasks and robot vs. voice agents to shape user outcomes in Human-Robot Interaction (HRI).


## Methodology
- **Participants:** 32  
- **Design:** Mixed-factorial (2×2×4)
    - **Between-subject factor:** Task type (2)
    - **Within-subject factors:** Agent embodiment (2) and feedback levels (4)
- **Tasks:** Creative shape design (promotion-focused) & error detection (prevention-focused)
- **Agents:** NAO robot and voice agent
- **Feedback Levels:** Task-learning, Task-motivation, Self, and No Feedback  
- **Feedback Generation:** Real-time, LLM-powered adaptive responses using `GPT-4o-mini` following Feedback Intervention Theory (FIT)

## Key Findings
- Task-learning feedback significantly improved performance in creative (promotion-focused) tasks, especially when delivered by the robot agent.
- Voice agents performed better in error detection (prevention-focused) tasks due to reduced distraction.
- Robot agents were perceived as more anthropomorphic and engaging but could be distracting in detailed, prevention-focused tasks.

## Insights
- The effectiveness of feedback depends on feedback level, task characteristics, and agent embodiment.
- Task-learning feedback consistently enhances both objective performance and perceived usefulness.
- Embodied robots boost engagement but may hinder accuracy in detailed, prevention-focused tasks.