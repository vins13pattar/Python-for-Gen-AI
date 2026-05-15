# PRD: MicroDegree Customer Support Chatbot Agent

## 1. Product Overview

**Product Name:** MicroDegree Customer Support Chatbot Agent
**Project Type:** Mini project / proof-of-concept
**Platform:** Web-based chatbot using Streamlit
**Target Website:** MicroDegree: https://www.microdegree.work/
**Goal:** Build a simple AI-powered customer support chatbot for MicroDegree that can answer common queries from prospective learners and existing learners using a Retrieval-Augmented Generation system.

MicroDegree publicly positions itself as a Kannada-focused tech skilling platform. Its course platform lists premium courses such as Python, MySQL, JavaScript Advanced, ReactJS, Web Development, Data Analytics, Frontend Development, Software Developer, Selenium, Aptitude, and MicroDegree Pro access.

The chatbot should answer questions about courses, certificates, doubt clarification, course access, Kannada-based learning, contact details, and general learner support using only the knowledge base loaded into ChromaDB.

## 2. Problem Statement

Prospective learners often ask repetitive questions before enrolling:
* What is MicroDegree?
* Are courses taught in Kannada?
* Which courses are available?
* Will learners get a certificate?
* How are doubts clarified?
* Is coding done in Kannada or English?
* How can someone contact MicroDegree?
* What is MicroDegree Pro?

Existing learners may also ask basic support questions about course access, completion, certificates, doubt support, and learning flow.

Currently, such queries may require manual human support. A lightweight chatbot can reduce repetitive support effort and provide quick, consistent answers.

## 3. Objectives

**Primary Objectives**
* Build a RAG-based customer support chatbot for MicroDegree.
* Use LangGraph to model the chatbot as a graph with nodes, edges, memory, and conditional routing.
* Use ChromaDB as the local vector database.
* Use Streamlit to create a simple chat UI.
* Support both prospective learners and existing learners.
* Avoid user authentication and persistent user account sessions.
* Provide grounded answers based on MicroDegree knowledge documents.

**Learning Objectives**
This mini project should help learners understand:
* LangGraph nodes and edges.
* LangGraph state management.
* Short-term memory in chatbot workflows.
* RAG architecture.
* ChromaDB vector storage.
* Streamlit chat interface development.
* Prompting an LLM with retrieved context.

## 4. Scope

**In Scope**
| Area | Description |
| :--- | :--- |
| Chat UI | Simple Streamlit-based chat interface |
| RAG | Retrieve MicroDegree-related knowledge from ChromaDB |
| LangGraph | Use nodes, edges, state, and memory |
| Vector DB | Use local ChromaDB persistence |
| Knowledge Base | Seed MicroDegree FAQ/course/support information |
| Memory | Maintain short-term conversation history during active chat |
| Guardrails | Avoid unsupported claims and redirect users to enquiry support when needed |
| No Auth | No login, registration, or user profile management |

**Out of Scope**
| Area | Reason |
| :--- | :--- |
| User login/authentication | Not required for mini project |
| Learner-specific progress tracking | Requires MicroDegree backend integration |
| Payment support | Avoid sensitive or transactional workflows |
| Refund automation | Should be handled by official support |
| CRM/ticket creation | Not required in MVP |
| Live human handoff | Can be added later |
| Admin dashboard | Not required in mini project |
| Real-time website crawling | MVP uses curated documents |

## 5. Target Users

### 5.1 Prospective Learners
Users who are interested in joining MicroDegree courses.

Common queries:
* “What courses are available?”
* “Is the course in Kannada?”
* “Do I get certificate?”
* “Is this suitable for beginners?”
* “How do I contact MicroDegree?”
* “What is MicroDegree Pro?”

### 5.2 Existing Learners
Users who have already enrolled.

Common queries:
* “How can I clarify doubts?”
* “How do I complete the course?”
* “Will I get a certificate?”
* “Do I need to submit projects?”
* “Where can I access the course?”

## 6. Key Public Knowledge to Support

The initial knowledge base should include the following confirmed public information:
* MicroDegree is a Kannada-focused tech skilling platform.
* The MicroDegree course site lists premium courses including Python, MySQL, JavaScript Advanced, ReactJS, Web Development, Data Analytics, Frontend Development, Software Developer, Automation Testing - Selenium, and Aptitude.
* MicroDegree Pro is described as unlimited access to 25+ e-learning courses at a single price on the public course page.
* Public FAQ content says courses are taught in Kannada for better understanding, while coding is done using standard IDEs in simple English.
* Public FAQ content says learners receive an e-certificate of completion after successfully finishing all modules.
* Public FAQ content mentions doubt clarification through Discord Community and weekly mentorship through free webinars.
* The MicroDegree course site lists enquiry number 08047109999; another public MicroDegree page lists phone +91 83108 82795 and email hello@microdegree.work.

## 7. Functional Requirements

**FR1: Chat Interface**
The system shall provide a simple Streamlit chat UI.
Requirements:
* Show chatbot title and description.
* Show previous messages in the current browser interaction.
* Accept user input through a chat input box.
* Display assistant responses in chat format.
* Show helpful fallback messages when answer is not found.
*(Streamlit officially provides chat elements such as st.chat_input and st.chat_message for conversational apps.)*

**FR2: Knowledge Ingestion**
The system shall provide an ingestion script to load MicroDegree support content into ChromaDB.
The ingestion process shall:
* Load Markdown/text knowledge files.
* Split documents into chunks.
* Generate embeddings.
* Store chunks in ChromaDB with metadata.
* Persist ChromaDB locally.

Example knowledge files:
```text
data/
  seed_microdegree.md
  faq.md
  courses.md
  contact.md
  support.md
```

**FR3: Vector Search**
The system shall retrieve relevant chunks from ChromaDB based on the learner’s question.
Retrieval requirements:
* Use top-k retrieval, default k = 4.
* Include metadata such as source filename and section.
* Return empty result if nothing relevant is found.
* Avoid answering from general LLM knowledge when relevant context is missing.
*(ChromaDB stores and indexes embeddings so similar content can be searched efficiently. LangChain also provides a Chroma vector store integration through the langchain-chroma package.)*

**FR4: LangGraph Workflow**
The chatbot shall be implemented as a LangGraph workflow.
LangGraph’s graph model uses nodes to perform work and edges to decide what happens next.

Required nodes:
| Node | Responsibility |
| :--- | :--- |
| extract_question | Read the latest user message |
| route_query | Identify whether the query is greeting, support query, or out-of-scope |
| retrieve_context | Search ChromaDB |
| grade_context | Decide whether retrieved context is useful |
| generate_answer | Generate grounded answer using retrieved context |
| fallback_answer | Respond when context is missing |
| greeting_response | Handle greetings and basic intro |
| out_of_scope_response | Handle irrelevant questions |

**FR5: Conditional Edges**
The graph shall use conditional edges for routing.

Example routing:
```text
START
  → extract_question
  → route_query
      ├── greeting_response
      ├── retrieve_context
      └── out_of_scope_response

retrieve_context
  → grade_context
      ├── generate_answer
      └── fallback_answer

generate_answer → END
fallback_answer → END
greeting_response → END
out_of_scope_response → END
```

**FR6: Memory**
The chatbot shall maintain short-term conversation memory during the active chat.
LangGraph supports short-term memory through checkpointing, and the official docs show InMemorySaver being used with StateGraph for thread-level memory.
For this mini project:
* Use InMemorySaver.
* Store conversation history in LangGraph state.
* No database-backed long-term memory.
* No user-specific saved memory.
* Memory resets when the Streamlit app/server restarts.

**FR7: Grounded Answer Generation**
The chatbot shall answer only using retrieved context.
Answer behavior:
* Be friendly and learner-focused.
* Prefer simple English.
* Include Kannada-friendly wording where useful.
* Do not invent course details.
* Do not invent prices, refund rules, coupon codes, placement guarantees, or payment details.
* If unsure, ask the user to contact MicroDegree support.

Example response style:
> MicroDegree teaches coding and job-ready tech skills in Kannada.
> Coding itself is done in standard IDEs using simple English, but the explanation is in Kannada for better understanding.
> For the latest course details, you can check the official MicroDegree course page or contact the enquiry team.

**FR8: Fallback Handling**
The chatbot shall provide a safe fallback if it cannot find enough context.

Fallback example:
> I could not find confirmed information about this in my MicroDegree knowledge base.
> Please contact MicroDegree directly for the latest and accurate details.
> Enquiry: 08047109999
> Email: hello@microdegree.work

**FR9: Source Awareness**
The chatbot should internally use retrieved document chunks as answer sources.
For MVP UI:
* Source display is optional.
* Developer logs may show retrieved source filenames.
* Advanced version may show “Sources used” below each answer.

## 8. Non-Functional Requirements

| Category | Requirement |
| :--- | :--- |
| Simplicity | Easy to run locally |
| Performance | Response should usually complete within a few seconds |
| Security | API keys must be loaded from .env, not hardcoded |
| Accuracy | Answers must be grounded in retrieved content |
| Maintainability | Clean folder structure with separate graph, vector store, config, and ingestion files |
| Cost Control | Use small embedding and chat models where possible |
| Privacy | No user authentication and no persistent learner profile storage |
| Reliability | If ChromaDB is missing, show clear setup instructions |

## 9. Technical Architecture

### 9.1 High-Level Architecture
```text
Learner
  ↓
Streamlit Chat UI
  ↓
LangGraph Support Agent
  ↓
Query Router Node
  ↓
Retriever Node
  ↓
ChromaDB Vector Store
  ↓
Relevant MicroDegree Chunks
  ↓
LLM Answer Generation Node
  ↓
Streamlit Response
```

### 9.2 Tech Stack
| Layer | Technology |
| :--- | :--- |
| UI | Streamlit |
| Agent Workflow | LangGraph |
| LLM Orchestration | LangChain |
| Vector Database | ChromaDB |
| Embeddings | OpenAI Embeddings |
| Chat Model | OpenAI chat model |
| Language | Python |
| Config | .env |
| Storage | Local ChromaDB folder |

## 10. Proposed Folder Structure
```text
microdegree-support-bot/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   └── seed_microdegree.md
├── chroma_db/
│   └── ...
└── src/
    ├── __init__.py
    ├── config.py
    ├── ingest.py
    ├── vectorstore.py
    ├── graph.py
    └── prompts.py
```

## 11. LangGraph State Design
```python
class SupportBotState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    route: str
    retrieved_docs: list
    context: str
    answer: str
    confidence: str
```

**State Fields**
| Field | Purpose |
| :--- | :--- |
| messages | Stores chat history |
| question | Latest user question |
| route | Query category |
| retrieved_docs | Documents from ChromaDB |
| context | Combined retrieved text |
| answer | Final chatbot response |
| confidence | Context confidence: high, medium, low |

## 12. LangGraph Node Design

**Node 1: extract_question**
Extract latest user message from state.
Input: `messages`
Output: `question`

**Node 2: route_query**
Classify user query.
Possible routes: `greeting`, `support_query`, `out_of_scope`

Examples:
| User Query | Route |
| :--- | :--- |
| “Hi” | greeting |
| “Do I get certificate?” | support_query |
| “Who is Virat Kohli?” | out_of_scope |

**Node 3: retrieve_context**
Search ChromaDB for matching knowledge chunks.
Input: `question`
Output: `retrieved_docs`, `context`

**Node 4: grade_context**
Check whether retrieved context is useful.
Logic:
* If no documents: low confidence.
* If similarity score is weak: low confidence.
* If documents match MicroDegree topic: high/medium confidence.
Output: `confidence`

**Node 5: generate_answer**
Generate final answer using:
* User question.
* Retrieved context.
* Conversation memory.
* Support bot system prompt.

**Node 6: fallback_answer**
Generate safe fallback when context is not enough.

**Node 7: greeting_response**
Respond to greetings.
Example: *Hi! I’m MicroDegree’s support assistant. I can help you with course details, certificates, Kannada learning, doubt clarification, MicroDegree Pro, and contact information.*

**Node 8: out_of_scope_response**
Politely reject unrelated questions.
Example: *I’m designed to help with MicroDegree course and learner support queries. Please ask me about courses, certificates, learning support, MicroDegree Pro, or contact details.*

## 13. Prompt Requirements

**System Prompt**
```text
You are MicroDegree Support Assistant.

Your job is to answer questions from prospective learners and existing learners about MicroDegree courses, learning support, certificates, Kannada-based learning, course access, and contact information.

Use only the provided context from the MicroDegree knowledge base.

Rules:
1. Do not invent course details.
2. Do not invent prices, discounts, refund policies, placement guarantees, or payment details.
3. If the answer is not available in the context, say that you do not have confirmed information.
4. Redirect the user to official MicroDegree support when needed.
5. Keep answers clear, friendly, and beginner-friendly.
6. Use simple English. You may include Kannada-friendly explanations where helpful.
7. Never claim that the user is enrolled because there is no authentication.
```

## 14. Sample Knowledge Base Content

The initial `seed_microdegree.md` should include:

```markdown
# MicroDegree Support Knowledge Base

## About MicroDegree
MicroDegree is a Kannada-focused tech skilling platform that teaches coding and job-ready technology skills.

## Language of Teaching
Courses are taught in Kannada to help learners understand programming concepts clearly. Coding is done using standard IDEs in simple English.

## Courses
MicroDegree offers courses such as Python, MySQL, JavaScript Advanced, ReactJS, Web Development, Data Analytics, Frontend Development, Software Developer, Automation Testing - Selenium, Aptitude, C Programming, HTML & CSS, and PHP.

## MicroDegree Pro
MicroDegree Pro provides access to multiple e-learning courses at a single price.

## Certificate
Learners receive an e-Certificate of Completion after successfully completing all course modules.

## Doubt Clarification
Doubts can be clarified through the community and mentorship support mentioned by MicroDegree.

## Contact
For latest course details, price, offers, and enrollment support, contact MicroDegree directly.
Enquiry: 08047109999
Email: hello@microdegree.work
```

## 15. User Stories

**Prospective Learner Stories**
| ID | User Story | Priority |
| :--- | :--- | :--- |
| US1 | As a prospective learner, I want to know what MicroDegree is so that I can decide if it is useful for me. | High |
| US2 | As a learner, I want to know whether courses are taught in Kannada. | High |
| US3 | As a learner, I want to know available courses. | High |
| US4 | As a learner, I want to know whether I will get a certificate. | High |
| US5 | As a learner, I want to know how doubts are clarified. | High |
| US6 | As a learner, I want contact details for enrollment support. | High |
| US7 | As a learner, I want to know about MicroDegree Pro. | Medium |

**Existing Learner Stories**
| ID | User Story | Priority |
| :--- | :--- | :--- |
| US8 | As an existing learner, I want to know how to complete my course. | Medium |
| US9 | As an existing learner, I want to know if projects are required for certificates. | Medium |
| US10 | As an existing learner, I want to know how to get help for access issues. | Medium |

## 16. Acceptance Criteria

**Chat UI**
* User can open Streamlit app.
* User can type a message.
* Assistant response appears in chat format.
* Previous messages remain visible during the active interaction.

**RAG**
* Knowledge base can be ingested into ChromaDB.
* User query retrieves relevant chunks.
* Bot uses retrieved chunks to answer.
* Bot does not answer unsupported questions confidently.

**LangGraph**
* Workflow uses multiple nodes.
* Workflow uses edges and conditional routing.
* Workflow uses memory/checkpointer.
* Graph handles greeting, support query, and out-of-scope query separately.

**Safety**
* Bot does not claim live backend access.
* Bot does not access learner account data.
* Bot does not invent prices or offers.
* Bot redirects to MicroDegree support when uncertain.

## 17. Example Conversations

**Example 1: Kannada Learning**
> **User:** Is coding taught in Kannada?
> **Bot:** MicroDegree explains programming concepts in Kannada so learners can understand the fundamentals clearly. Coding itself is done using standard IDEs in simple English.

**Example 2: Certificate**
> **User:** Will I get certificate after course?
> **Bot:** Yes. Based on the MicroDegree FAQ, learners receive an e-Certificate of Completion after successfully finishing all the modules in the course.

**Example 3: Doubt Clarification**
> **User:** How can I ask doubts?
> **Bot:** MicroDegree mentions doubt clarification through its learner community and mentorship support. For the latest support process, you can contact MicroDegree directly.

**Example 4: Out of Scope**
> **User:** Tell me today’s cricket score.
> **Bot:** I’m designed to help with MicroDegree course and learner support queries. Please ask me about courses, certificates, Kannada learning, MicroDegree Pro, or contact details.

**Example 5: Unknown Information**
> **User:** Can I get 90% discount today?
> **Bot:** I don’t have confirmed information about current discounts or offers in my knowledge base. Please contact MicroDegree directly for the latest pricing and offers.
> Enquiry: 08047109999

## 18. Implementation Milestones

**Milestone 1: Project Setup**
Deliverables:
* Python virtual environment
* requirements.txt
* .env.example
* Folder structure

**Milestone 2: Knowledge Base**
Deliverables:
* data/seed_microdegree.md
* Document loader
* Text splitter
* Metadata structure

**Milestone 3: ChromaDB Ingestion**
Deliverables:
* src/ingest.py
* Local ChromaDB persistence
* Re-ingestion command
Command: `python -m src.ingest`

**Milestone 4: LangGraph Agent**
Deliverables:
* State schema
* Nodes
* Conditional edges
* Memory checkpointer
* Graph compilation

**Milestone 5: Streamlit UI**
Deliverables:
* app.py
* Chat input
* Chat message rendering
* Error handling
* Clear chat button

**Milestone 6: Testing**
Deliverables:
* Test questions
* Expected answers
* Out-of-scope test cases
* Fallback test cases

## 19. Testing Plan

**Test Case Matrix**
| Test Case | Input | Expected Behavior |
| :--- | :--- | :--- |
| TC1 | Hi | Greeting response |
| TC2 | What is MicroDegree? | Answers from KB |
| TC3 | Are courses in Kannada? | Explains Kannada teaching and English coding |
| TC4 | Do I get certificate? | Certificate answer from KB |
| TC5 | What courses are available? | Lists known courses |
| TC6 | How can I contact MicroDegree? | Shows enquiry/contact details |
| TC7 | Give me refund policy | Fallback if not in KB |
| TC8 | Tell me cricket score | Out-of-scope response |
| TC9 | What did I ask before? | Uses short-term memory |
| TC10 | What is MicroDegree Pro? | Answers from KB |

## 20. Success Metrics

| Metric | Target |
| :--- | :--- |
| Correct answers for known FAQ queries | 80%+ in mini-project testing |
| Unsupported query fallback accuracy | 90%+ |
| App startup success | 100% after setup |
| Average local response time | Under 10 seconds, depending on model/network |
| Hallucinated pricing/claims | 0 accepted cases |

## 21. Risks and Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Outdated knowledge base | Wrong answers | Keep seed documents updated manually |
| LLM hallucination | Misleading learner | Strong system prompt and context-only answering |
| Missing ChromaDB index | App failure | Add clear error message asking to run ingestion |
| No authentication | Cannot answer learner-specific queries | Clearly state that account-specific support is unavailable |
| Public site changes | Stale data | Periodically update knowledge files |

## 22. Future Enhancements

* Add website crawler for MicroDegree pages.
* Add source citations in UI.
* Add Kannada response mode.
* Add admin page to upload FAQs.
* Add WhatsApp integration.
* Add support ticket creation.
* Add learner login and account-specific help.
* Add analytics for unanswered questions.
* Add hybrid search using keyword + vector retrieval.
* Add human handoff for complex support queries.

## 23. Final MVP Definition

The MVP is complete when:
* Streamlit chat UI is working.
* MicroDegree knowledge base is ingested into ChromaDB.
* LangGraph workflow uses nodes, edges, conditional routing, and memory.
* Bot answers common MicroDegree learner queries.
* Bot safely rejects out-of-scope questions.
* Bot gives fallback support contact when information is missing.
* No authentication or persistent user sessions are implemented.
