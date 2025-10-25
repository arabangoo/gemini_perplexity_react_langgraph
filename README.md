## [Gemini Perplexity React LangGraph 풀스택 웹페이지]    
   
본 테스트의 목표는 Gemini-React-LangGraph를 이용한 풀스택 웹페이지를 구축하는 것이다.   
본 테스트에는 Gemini API 키와 Perplexity API 키가 필요하니 미리 발급받아 놓자.   
   
본 테스트의 방향대로 구축이 완료되면 로컬 PC에서 아래와 같은 기능의 서비스를 사용할 수 있다.   
1. Perplexity 최신 검색   
2. Gemini 심층 분석   
3. 세션 기반 대화 기억   
4. 브라우저 닫으면 삭제         
<br/>
   
(1) 윈도우 로컬 PC에서 서비스를 올려보도록 하겠다.   
아래와 같은 명령어로 필수 프로그램의 버전을 먼저 확인해본다.          
   
명령어 (1)  : python --version
명령어 (2) : node --version
명령어 (3) : npm --version
<img width="500" height="160" alt="image_1" src="https://github.com/user-attachments/assets/c2453554-2cc6-42e4-b172-1acfe3b53084" />
<br/><br/>
                   
(2) GitHub 리포지토리에 올라가 있는 파일 구성은 아래와 같다.   
```txt
├── 실행 관련 파일들 
│   ├── install.bat          ← 의존성 설치 자동화
│   ├── run-backend.bat      ← 백엔드만 실행
│   ├── run-frontend.bat     ← 프론트엔드만 실행
│   ├── run-all.bat          ← 백엔드+프론트엔드 동시 실행
│   ├── docker-deploy.bat    ← Docker로 배포
│
├── Docker 관련
│   ├── Dockerfile          
│   ├── docker-compose.yml   ← Perplexity API 키 추가
│   └── .env                 ← Docker용 환경 변수
│
├── Backend (백엔드)
│   └── backend/
│       ├── .env             ← API 키 설정 (핵심!)
│       ├── pyproject.toml   ← httpx 의존성 추가
│       └── src/
│           ├── agent/
│           │   ├── app.py       ← FastAPI 서버 
│           │   ├── graph.py     ← LangGraph 워크플로우 
│           │   └── state.py     ← ResearchState 추가
│           └── tools/
│               └── perplexity.py ← Perplexity 검색 도구 
│
└── Frontend (프론트엔드)
    └── frontend/
        └── src/
            └── App.tsx      ← React 컴포넌트
```
<br/>
        
(3) 백엔드 핵심 파일 설명   
[backend/.env] - Gemini API와 Perplexity API를 사용하기 위한 인증 키   
```txt
GEMINI_API_KEY=실제 제미나이 API 키 기입   
PERPLEXITY_API_KEY=실제 퍼플렉시티 API 키 기입   
HOST=0.0.0.0   
PORT=8000
```

[backend/src/tools/perplexity.py] - 사용자 질문을 받아 퍼플렉시티 API를 호출해 웹 검색 실행   
```txt
@tool
async def perplexity_search(query: str, search_recency: str) -> dict:   
"""Perplexity API로 최신 웹 정보를 검색합니다"""
```  

[backend/src/agent/state.py] - 워크플로우 전체에서 사용하는 상태 구조 정의   
```txt
class ResearchState(TypedDict):   
messages: list[BaseMessage]    # 대화 기록 (MemorySaver가 저장)   
query: str                     # 사용자 질문   
search_results: list[dict]     # Perplexity 검색 결과 누적   
citations: list[str]           # 출처 URL 목록   
related_questions: list[str]   # 관련 질문   
analysis: str                  # Gemini 분석 결과   
final_answer: str              # 최종 답변   
iteration: int                 # 검색 횟수 (최대 3회)   
needs_more_research: bool      # 재검색 필요 여부   
- 각 노드가 이 State를 읽고 수정하며 전달   
- MemorySaver가 messages 필드를 세션별로 저장
```
   
**[backend/src/agent/graph.py]** - LangGraph 워크플로우 정의 (핵심 로직)   
```txt
흐름: extract_query → search_perplexity → analyze_with_gemini   
→ should_continue → (재검색 or generate_final_answer)
```
   
1. extract_query: 질문 추출 및 State 초기화   
2. search_perplexity: Perplexity로 웹 검색, 결과 누적   
3. analyze_with_gemini: Gemini가 "정보 충분한가?" 판단   
4. should_continue: 조건 분기 (재검색 vs 답변 생성)   
5. generate_final_answer: 모든 검색 결과 종합하여 최종 답변 생성   
6. MemorySaver: 대화 기록을 RAM에 저장 (세션별, 휘발성)   
   
[backend/src/agent/app.py] - FastAPI 서버 및 API 엔드포인트      
```txt
@app.post("/api/research")   
async def research(request: QueryRequest):   
    # 1. 세션 ID 확인/생성   
    # 2. LangGraph 워크플로우 실행   
    # 3. 결과 반환 (answer, citations, related_questions, iterations)
```
             
1. 프론트엔드에서 POST 요청 받음   
2. session_id로 MemorySaver에서 이전 대화 로드   
3. 워크플로우 실행 후 JSON 응답   
4. CORS 설정으로 프론트엔드(5173) 접근 허용   
<br/>

(4) 프론트엔드 핵심 파일 설명 
[frontend/src/App.tsx]
```txt
export default function App() {
const [messages, setMessages] = useState<Message[]>([])
const [sessionId, setSessionId] = useState<string | null>(null)
// 세션 ID 생성 (브라우저별 고유)
useEffect(() => {
let sid = sessionStorage.getItem('chat_session_id')
if (!sid) {
sid = generateUUID()
sessionStorage.setItem('chat_session_id', sid)
}
setSessionId(sid)
}, [])
// 메시지 전송
const handleSubmit = async () => {
const response = await axios.post(${API_URL}/api/research, {
query: input,
session_id: sessionId
})
setMessages([...messages, assistantMessage])
}
}
```
   
UI 구성:   
1. Header - 제목 + "새 대화" 버튼   
2. Chat Area - 대화 메시지들   
3. 사용자 메시지 - 파란색 오른쪽 화면   
4. AI 답변 - 회색 왼쪽 화면 + 출처 + 관련 질문   
5. Input Area - 질문 입력 + 전송 버튼   
   
세션 관리:   
1. sessionStorage에 session_id 저장   
2. 같은 탭에서는 계속 같은 세션 유지   
3. 새 탭 열면 새 세션 생성   
4. "새 대화" 버튼 누르면 새 세션 생성   
<br/>
      
(5) 실행 스크립트들 (배치 파일)
[install.bat] - 의존성 설치
```txt
cd backend
pip install -e .

cd frontend
npm install
```
   
[run-backend.bat] - 백엔드 실행   
```txt
cd backend
langgraph dev
```
   
**역할:**   
- LangGraph 개발 서버 시작   
- FastAPI 서버 실행 (포트 2024 - 로컬 개발 모드 기본값)    
- 핫 리로드 지원 (코드 수정하면 자동 재시작)   
* Docker 배포시에는 포트 8123 사용

[run-frontend.bat] - 프론트엔드 실행   
```txt
cd frontend
npm run dev
```
   
**역할:**   
- Vite 개발 서버 시작 (포트 5173)   
- React 앱 실행   
- 핫 리로드 지원 (코드 수정하면 자동 재시작)

[run-all.bat] - 전체 동시 실행   
```txt
start "Backend" cmd /k "cd backend && langgraph dev"
start "Frontend" cmd /k "cd frontend && npm run dev"
```

[docker-deploy.bat] - Docker 배포, 로컬 실행시에는 필요 없음.   
```txt
docker build -t gemini-fullstack-langgraph .
docker-compose up -d
```
   
역할:   
1. Docker 이미지 빌드 (프론트+백엔드 통합)   
2. PostgreSQL, Redis, API 서버 모두 시작   
3. 프로덕션 배포용   
      
사용:   
1. 로컬 개발이 아닌 실제 배포할 때   
2. 서버에 올릴 때   
3. 모든 걸 컨테이너로 격리하고 싶을 때
   
[docker-compose.yml]
```txt
environment:
GEMINI_API_KEY: ${GEMINI_API_KEY}
PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}
```
    
1. Docker 컨테이너 안에서도 Perplexity API 키 필요   
2. 루트 `.env` 파일에서 읽어옴   
<br/>

(6) 서비스 워크플로우   
### 로컬 개발 모드 (run-all.bat 실행 시)   
1. 사용자가 run-all.bat 더블클릭       
2. 백엔드 CMD 창 열림      
	- backend/.env 파일 읽음 (API 키 로드)      
	- research_graph 생성 (MemorySaver 초기화)      
	- FastAPI 서버 시작 (로컬 개발 환경 포트 2024)       
3. 프론트엔드 CMD 창 열림      
	- Vite 서버 시작 (포트 5173)      
	- React 앱 빌드    
4. 브라우저에서 http://localhost:5173 접속    
5. 사용자가 질문 입력 ("AWS ECS vs EKS?")    
6. 프론트엔드가 백엔드로 POST /api/research 요청 { "query": "AWS ECS vs EKS?", "session_id": "abc123" }    
7. 백엔드 워크플로우 실행: extract_query → search_perplexity → analyze_with_gemini → (부족하면 재검색) → generate_final_answer    
8. 백엔드가 JSON 응답: { "answer": "ECS는...", "citations": ["https://aws.amazon.com/..."], "related_questions": ["EKS의 비용은?"], "iterations": 2, "session_id": "abc123" }    
10. 프론트엔드가 답변 화면에 표시   
	- 마크다운 렌더링   
	- 출처 링크   
	- 관련 질문 버튼     
11. MemorySaver에 대화 저장 (세션별)   
	- 다음 질문할 때 이전 대화 기억   
<br/>

(7) 서비스 구성 및 절차 요약    
구성 요약:   
1. Perplexity 도구: 최신 웹 정보 검색   
2. Gemini 분석: 검색 결과 분석 + 답변 생성   
3. LangGraph 워크플로우: 자동 재검색 로직   
4. MemorySaver: 대화 기억 (휘발성)   
5. React 프론트엔드: 깔끔한 채팅 UI   
6. 배치 파일들: 실행 자동화
   
절차 요약:   
1. install.bat (최초 1회)   
2. run-all.bat (매번)   
3. 브라우저에서 http://localhost:5173   
<br/>

(8) 위에서 말한 절차대로 윈도우 cmd 창에서 명령어를 실행한다.   
cmd 창은 관리자 권한으로 실행해주는 것을 추천한다.   

명령어 (1)  : install.bat   
명령어 (2) : run-all.bat   
<br/>

(9) 위에서 말한 절차대로 윈도우 cmd 창에서 명령어를 실행한다.   
cmd 창은 관리자 권한으로 실행해주는 것을 추천한다.   
<img width="800" height="500" alt="image_2" src="https://github.com/user-attachments/assets/e4599165-16ab-43f4-93d8-e8de0ac974bb" />
<br/>

(10) 명령어가 정상적으로 실행되면 웹브라우저에서 "http://localhost:5173" 주소로 접속시 아래와 같은 화면이 열리는 것을 확인할 수 있다.   
<img width="800" height="500" alt="image_3" src="https://github.com/user-attachments/assets/1aba65ee-632e-492b-9c31-8b9e92d07871" />
<br/><br/>

(11) AI와 소통하게 되면 기존 LLM 응답과는 달리 최신 정보를 바탕으로 응답해주는 것을 알 수 있다.               
<img width="800" height="500" alt="image_4" src="https://github.com/user-attachments/assets/268525d2-8f36-4c51-92b3-374bc7aedd7f" />
<br/><br/>

(12) GitHub 리포지토리의 코드를 복사해서 각자 로컬 PC에서 활용하기 위해서는 아래 3개 파일을 수정해야 한다.    

[C:\실제 경로\ 경로의 .env 파일 수정]   
- 실제 제미나이 API 키와 실제 퍼플렉시티 API 키를 기입한다.   
- 로컬 PC에서 서비스를 쓸 경우 랭스미스 API 키는 기입할 필요 없다.
<img width="500" height="300" alt="image_5" src="https://github.com/user-attachments/assets/5f62309a-76a8-4f28-a3f1-64f1b37091d9" />
<br/>
[C:\실제 경로\backend 경로의 .env 파일 수정]      
- 실제 제미나이 API 키와 실제 퍼플렉시티 API 키를 기입한다.   
<img width="500" height="300" alt="image_6" src="https://github.com/user-attachments/assets/cf3b2fe6-ad48-47be-bbe0-3a506a7c8827" />
<br/>
[C:\실제 경로\ 경로의 run-all.bat 파일 수정]   
- "실제 경로"라고 적힌 부분을 폴더가 있는 실제 경로로 바꿔서 기입한다.   
<img width="800" height="400" alt="image_7" src="https://github.com/user-attachments/assets/ad3afd23-f957-44aa-9be8-7ad07a6b9a3a" />







