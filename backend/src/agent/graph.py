"""Perplexity + Gemini Research Agent (MemorySaver)"""
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
# MemorySaver 제거 - LangGraph API가 persistence 자동 처리
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from agent.state import ResearchState
from tools.perplexity import perplexity_search

# Gemini 초기화
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment")

gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0.3,
    api_key=GEMINI_API_KEY
)

def extract_query(state: ResearchState) -> ResearchState:
    """사용자 메시지에서 쿼리 추출"""
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            state["query"] = last_message.content
    state.setdefault("iteration", 0)
    state.setdefault("search_results", [])
    state.setdefault("citations", [])
    state.setdefault("related_questions", [])
    return state


async def search_perplexity(state: ResearchState) -> ResearchState:
    """Perplexity로 웹 검색"""
    query = state["query"]
    print(f"\n🔍 [검색 {state['iteration'] + 1}] Perplexity: {query}")
    result = await perplexity_search.ainvoke({"query": query, "search_recency": "month"})
    if "error" in result:
        print(f"❌ 검색 실패: {result['error']}")
        result = {"content": "", "citations": [], "related_questions": []}
    state["search_results"].append(result)
    state["citations"].extend(result.get("citations", []))
    state["related_questions"] = result.get("related_questions", [])
    state["iteration"] += 1
    print(f"✅ 검색 완료: {len(result.get('citations', []))}개 출처")
    return state

async def analyze_with_gemini(state: ResearchState) -> ResearchState:
    """Gemini로 검색 결과 분석"""
    query = state["query"]
    all_content = "\n\n".join([r.get('content', '') for r in state["search_results"] if r.get('content')])
    if not all_content:
        state["analysis"] = "No results"
        state["needs_more_research"] = False
        return state
    print(f"\n🧠 Gemini 분석 중...")
    prompt = f"질문: {query}\n\n검색결과:\n{all_content}\n\n정보가 충분하면 SUFFICIENT: YES, 부족하면 SUFFICIENT: NO"
    try:
        response = await gemini.ainvoke([HumanMessage(content=prompt)])
        state["analysis"] = response.content
        state["needs_more_research"] = "SUFFICIENT: NO" in response.content.upper() and state["iteration"] < 3
        print(f"✅ 분석 완료 | 추가 검색: {state['needs_more_research']}")
    except Exception as e:
        print(f"❌ Gemini 오류: {str(e)}")
        state["analysis"] = f"Error: {str(e)}"
        state["needs_more_research"] = False
    return state


async def generate_final_answer(state: ResearchState) -> ResearchState:
    """최종 답변 생성"""
    query = state["query"]
    all_content = "\n\n".join([r.get('content', '') for r in state["search_results"] if r.get('content')])
    print(f"\n📝 최종 답변 생성 중...")
    if not all_content:
        answer = "검색 결과를 찾을 수 없습니다. 다시 시도해주세요."
    else:
        prompt = f"질문: {query}\n\n검색 정보:\n{all_content}\n\n명확하고 전문적인 한국어 답변을 작성하세요:"
        try:
            response = await gemini.ainvoke([HumanMessage(content=prompt)])
            answer = response.content
        except Exception as e:
            print(f"❌ 답변 생성 오류: {str(e)}")
            answer = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
    citations = list(set(state["citations"]))
    if citations:
        answer += "\n\n---\n**📚 참고 출처:**\n"
        for i, cite in enumerate(citations[:10], 1):
            answer += f"\n[{i}] {cite}"
    if state.get("related_questions"):
        answer += "\n\n---\n**🔗 관련 질문:**\n"
        for q in state["related_questions"][:5]:
            answer += f"\n• {q}"
    state["final_answer"] = answer
    state["messages"].append(AIMessage(content=answer))
    print(f"✅ 최종 답변 완료")
    return state

def should_continue(state: ResearchState) -> Literal["search", "answer"]:
    """추가 검색 필요 여부"""
    return "search" if state.get("needs_more_research", False) else "answer"

def create_research_graph():
    """리서치 에이전트 그래프 생성 (LangGraph API 호환)"""
    workflow = StateGraph(ResearchState)
    workflow.add_node("extract", extract_query)
    workflow.add_node("search", search_perplexity)
    workflow.add_node("analyze", analyze_with_gemini)
    workflow.add_node("answer", generate_final_answer)
    workflow.add_edge(START, "extract")
    workflow.add_edge("extract", "search")
    workflow.add_edge("search", "analyze")
    workflow.add_conditional_edges("analyze", should_continue, {"search": "search", "answer": "answer"})
    workflow.add_edge("answer", END)
    print("💾 대화 저장: LangGraph API 자동 관리")
    return workflow.compile()  # checkpointer 제거 - LangGraph API가 자동 처리

research_graph = create_research_graph()
graph = research_graph  # langgraph.json 호환성을 위한 alias
